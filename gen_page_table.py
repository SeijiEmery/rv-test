#!/usr/bin/env python3
#
# Page table generator
#
# (c) Copyright 2018 Ethan L. Miller
#
# For use by students in CMPE 110, Fall 2018 at the University of California, Santa Cruz
# All other use requires written permission.
#

import sys
import argparse

def make_page_table (page_mappings,
                     bits_per_page = 12, l1_table_bits = 10, address_length = 32,  pte_length = 4):
    page_table = dict()
    l2_table_bits = address_length - l1_table_bits - bits_per_page
    l2_mask = (1 << l2_table_bits) - 1
    pte_valid_bit = 1 << (pte_length * 8 - 1)
    for m in page_mappings:
        (vpn, ppn) = m
        l1_entry = vpn >> l2_table_bits
        if l1_entry not in page_table:
            page_table[l1_entry] = dict()
        l2_entry = vpn & l2_mask
        page_table[l1_entry][l2_entry] = ppn
    for i in range (1 << l1_table_bits):
        if i not in page_table:
            page_table[i] = None       # mark invalid, since no L2 table
        else:
            for j in range (1 << l2_table_bits):
                if j not in page_table[i]:
                    page_table[i][j] = 0
                else:
                    page_table[i][j] |= pte_valid_bit
    return page_table

def get_leaf_page_table (leaf_page_table, pte_length = 4):
    '''
    Takes a single leaf page table, as generated above, and converts it to
    a byte string.
    '''
    b = list()
    i = 0
    while (i in leaf_page_table):
        b.append (leaf_page_table[i].to_bytes(pte_length, byteorder='little'))
        i += 1
    return b''.join (b)

def get_root_page_table (page_table, leaf_page_table_bases, pte_length = 4):
    '''
    Takes an entire page table and returns a byte string suitable for
    use as a root page table.  The base addresses of the leaf page tables
    (as physical page numbers) are passed as a sequence, and filled into the
    root page table.
    '''
    i = 0
    b = list()
    # Copy page list so we don't destroy the original
    pages = list(leaf_page_table_bases)
    pte_valid_bit = (1 << (pte_length * 8 - 1))
    while (i in page_table):
        if not page_table[i]:
            b.append ((0).to_bytes(pte_length, byteorder='little'))
        else:
            b.append ((pages.pop (0) | pte_valid_bit).to_bytes (pte_length, byteorder='little'))
        i += 1
    return b''.join (b)

def dump_binary_to_file (b, base_address, fp):
    for i in range (0, len (b), 16):
        print ('%08o' % (base_address + i), ' '.join (['%02x' % (v) for v in b[i:i+16]]), file=fp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser ()
    parser.add_argument('pagemappings', metavar='(vpn,ppn)', type=str, nargs='+', help='Page mapping from VPN to PPN')
    parser.add_argument('--tablepages', metavar='ppn', type=int, nargs='+', help='Physical pages for page tables')
    parser.add_argument('--rootpagetable', metavar='ppn', type=int, default=1000, help='Physical page for root page table')
    parser.add_argument('--output', metavar='file', type=str, default='-', help='Output file for loading into the simulator')
    args = parser.parse_args()
    try:
        if args.output == '-':
            fp = sys.stdout
        else:
            fp = open (args.output, "w")
    except:
        print ("Unable to open {0}".format (args.output), file=sys.stderr)
        sys.exit (1)
    mappings = ([(int(z[0]), int(z[1])) for z in [x.split (',') for x in args.pagemappings]])
    page_table = make_page_table (mappings)
    pt_pages = list (args.tablepages)
    for i in range (len (page_table)):
        if not page_table[i]: continue
        dump_binary_to_file (get_leaf_page_table (page_table[i]), pt_pages.pop (0) << 12, fp)
    dump_binary_to_file (get_root_page_table (page_table, args.tablepages), args.rootpagetable << 12, fp)
