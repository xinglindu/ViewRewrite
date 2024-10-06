copy region from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/region.tbl' with delimiter as '|' NULL '';
copy nation from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/nation.tbl' with delimiter as '|' NULL '';
copy partsupp from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/partsupp.tbl' with delimiter as '|' NULL '';
copy customer from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/customer.tbl' with delimiter as '|' NULL '';
copy lineitem from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/lineitem.tbl' with delimiter as '|' NULL '';
copy orders from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/orders.tbl' with delimiter as '|' NULL '';
copy part from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/part.tbl' with delimiter as '|' NULL '';
copy supplier from '/var/lib/postgresql/TPC-H-2.18.0_rc2/dbgen/tbl/supplier.tbl' with delimiter as '|' NULL '';