
SRCS = $(CURDIR)/generate_page_table.c
TABLE_SPEC = $(CURDIR)/page_table_layout
PAGE_TABLE = $(CURDIR)/page_table.bin
HEX_TABLE = $(CURDIR)/page_table.hex
GENERATOR = $(CURDIR)/generate_page_table

DEBUG ?=
CFLAGS = -Wall -pedantic $(DEBUG)

.PHONY: all default clean

default: all

all: $(HEX_TABLE)

$(HEX_TABLE): $(PAGE_TABLE)
	od -t x1 -v $^ > $@

$(PAGE_TABLE): $(GENERATOR) $(TABLE_SPEC)
	$(GENERATOR) 0 $(TABLE_SPEC) > $@

$(GENERATOR): $(SRCS)
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(PAGE_TABLE) $(HEX_TABLE) $(GENERATOR)
