
#include <stdio.h>
#include <errno.h>
#include <err.h>
#include <stdlib.h>
#include <ctype.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

// must sum to 32
#define PAGE_BITS	12
#define LEVEL_1_BITS	10
#define LEVEL_2_BITS	10

#define PAGE_SIZE	(1ULL << PAGE_BITS)
#define PAGE_MASK	(PAGE_SIZE - 1)

#define LEVEL_1_ENTRIES	(1ULL << LEVEL_1_BITS)
#define LEVEL_1_SIZE	(LEVEL_1_ENTRIES * sizeof(uint32_t))

#define LEVEL_2_ENTRIES	(1ULL << LEVEL_2_BITS)
#define LEVEL_2_SIZE	(LEVEL_2_ENTRIES * sizeof(uint32_t))

#define VALID_BIT_MASK	0x80000000

static uint32_t lvl_1_pt[LEVEL_1_ENTRIES] = { 0, };
static uint32_t *lvl_2_pts[LEVEL_1_ENTRIES] = { NULL, };

struct page_mapping {
	uint32_t vaddr;
	uint32_t paddr;
};

int parse_address(const char *str, uint32_t *res) {
	unsigned long long tmp;
	char *endp;

	errno = 0;
	tmp = strtoull(str, &endp, 0);
	if (endp == str) {
		errno = EINVAL;
		return -1;
	}
	if (errno)
		return -1;

	// illegally set high-order bit
	if (tmp & ~((1ULL << 32) - 1)) {
		errno = ERANGE;
		return -1;
	}

	*res = (uint32_t) tmp;

	return 0;
}

static inline void skip_space(char **str_p) {
	while (isspace(**str_p))
		++*str_p;
}

#define WHITESPACE	" \t\r\n"
int parse_mapping(const char *orig_str, struct page_mapping *res) {
	char *save;
	char *str;
	char *cur;
	char *vaddr_str;
	char *paddr_str;
	uint32_t vaddr;
	uint32_t paddr;
	int ret = -1;

	if (!(str = strdup(orig_str))) {
		warn("error allocating memory for line");
		return -1;
	}

	cur = str;
	skip_space(&cur);
	if (!*cur || *cur == '#') {
		ret = 0;
		goto fail;
	}

	if (!(vaddr_str = strtok_r(cur, WHITESPACE, &save)) ||
	    !(paddr_str = strtok_r(NULL, WHITESPACE, &save))) {
		warnx("invalid mapping: '%s'", orig_str);
		goto fail;
	}

	if (parse_address(vaddr_str, &vaddr)) {
		warn("invalid address: '%s'", vaddr_str);
		goto fail;
	}

	if (parse_address(paddr_str, &paddr)) {
		warn("invalid address: '%s'", paddr_str);
		goto fail;
	}

	if (vaddr & PAGE_MASK) {
		warnx("zeroing low-order bits in %s", vaddr_str);
		vaddr &= ~PAGE_MASK;
	}

	if (paddr & PAGE_MASK) {
		warnx("zeroing low-order bits in %s", paddr_str);
		paddr &= ~PAGE_MASK;
	}

	res->vaddr = vaddr;
	res->paddr = paddr;

	return 1;

   fail:
	free(str);

	return ret;
}

void read_input(FILE *in, struct page_mapping **mappings_out, size_t *n_mappings_out) {
	char *line;
	size_t line_size;
	ssize_t line_len;
	struct page_mapping *mappings;
	size_t n_mappings;
	struct page_mapping map;
	void *tmp;

	line = NULL;
	line_size = 0;
	mappings = NULL;
	n_mappings = 0;
	while ((line_len = getline(&line, &line_size, in)) >= 0) {
		if (line_len > 0 && line[line_len-1] == '\n')
			line[line_len-1] = '\0';

		if (parse_mapping(line, &map) <= 0)
			continue;

		if (!(tmp = realloc(mappings, sizeof(*mappings) * (n_mappings+1))))
			err(EXIT_FAILURE, "cannot allocate memory for mapping list");
		mappings = tmp;

		mappings[n_mappings++] = map;
	}
	free(line);
	if (ferror(in))
		err(EXIT_FAILURE, "error reading input file");

	*mappings_out = mappings;
	*n_mappings_out = n_mappings;
}

static inline uint32_t level_1_index(uint32_t addr) {
	return addr >> (PAGE_BITS + LEVEL_2_BITS);
}

static inline uint32_t level_2_index(uint32_t addr) {
	return (addr >> PAGE_BITS) & ((1ULL << LEVEL_2_BITS) - 1);
}

static inline void pt_set_valid(uint32_t *pt, unsigned index) {
	pt[index] |= VALID_BIT_MASK;
}

static inline uint32_t address_to_page_number(uint32_t addr) {
	return addr >> PAGE_BITS;
}

int vaddr_compare(const void *a_in, const void *b_in) {
	const struct page_mapping *a = (struct page_mapping *) a_in;
	const struct page_mapping *b = (struct page_mapping *) b_in;

	if (a->vaddr < b->vaddr)
		return -1;
	else if (a->vaddr == b->vaddr)
		return 0;
	else
		return 1;
}

int main(int argc, const char **argv) {
	FILE *in = stdin;
	uint32_t base_address;
	struct page_mapping *mappings;
	size_t n_mappings;
	size_t i;
	uint32_t l1_index;
	uint32_t l2_index;
	uint32_t l2_base;
	uint32_t next_l2_base;

	if (argc > 3 || argc < 2)
		errx(EXIT_FAILURE, "usage: generate_page_table <base address> [<mappings file>]");

	if (argc == 3 && !(in = fopen(argv[2], "r")))
		err(EXIT_FAILURE, "error opening input file %s", argv[2]);

	if (parse_address(argv[1], &base_address))
		errx(EXIT_FAILURE, "invalid base address '%s'", argv[1]);

	if (base_address & PAGE_MASK) {
		warnx("zeroing low-order bits in base address %s", argv[1]);
		base_address &= ~PAGE_MASK;
	}

	read_input(in, &mappings, &n_mappings);

	qsort(mappings, n_mappings, sizeof(*mappings), &vaddr_compare);

	next_l2_base = base_address + LEVEL_1_SIZE;
	for (i = 0; i < n_mappings; ++i) {
		l1_index = level_1_index(mappings[i].vaddr);
		l2_index = level_2_index(mappings[i].vaddr);

		if (!lvl_2_pts[l1_index]) {
			if (!(lvl_2_pts[l1_index] = malloc(LEVEL_2_SIZE)))
				errx(EXIT_FAILURE, "error allocating memory for second-level page table");
			l2_base = next_l2_base;
			next_l2_base += LEVEL_2_SIZE;
		}

		pt_set_valid(lvl_1_pt, l1_index);
		lvl_1_pt[l1_index] |= address_to_page_number(l2_base);

		pt_set_valid(lvl_2_pts[l1_index], l2_index);
		lvl_2_pts[l1_index][l2_index] |= address_to_page_number(mappings[i].paddr);
	}

	if (fwrite(lvl_1_pt, 1, LEVEL_1_SIZE, stdout) != LEVEL_1_SIZE)
		err(EXIT_FAILURE, "error writing output");
	for (i = 0; i < LEVEL_1_ENTRIES; ++i) {
		if (!lvl_2_pts[i])
			continue;

		if (fwrite(lvl_2_pts[i], 1, LEVEL_2_SIZE, stdout) != LEVEL_2_SIZE)
			err(EXIT_FAILURE, "error writing output");
	}

	return 0;
}
