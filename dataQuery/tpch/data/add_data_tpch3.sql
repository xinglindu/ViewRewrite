copy region from '/var/lib/postgresql/tpc-h-10/region.tbl' with delimiter as '|' NULL '';
copy nation from '/var/lib/postgresql/tpc-h-10/nation.tbl' with delimiter as '|' NULL '';
copy partsupp from '/var/lib/postgresql/tpc-h-10/partsupp.tbl' with delimiter as '|' NULL '';
copy customer from '/var/lib/postgresql/tpc-h-10/customer.tbl' with delimiter as '|' NULL '';
copy lineitem from '/var/lib/postgresql/tpc-h-10/lineitem.tbl' with delimiter as '|' NULL '';
copy orders from '/var/lib/postgresql/tpc-h-10/orders.tbl' with delimiter as '|' NULL '';
copy part from '/var/lib/postgresql/tpc-h-10/part.tbl' with delimiter as '|' NULL '';
copy supplier from '/var/lib/postgresql/tpc-h-10/supplier.tbl' with delimiter as '|' NULL '';