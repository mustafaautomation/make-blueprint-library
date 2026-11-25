"""Long-tail scenarios compiled from the record lists."""

from makebp.specs.expand import build_rest
from makebp.specs.rest_a import A
from makebp.specs.rest_b import B
from makebp.specs.rest_c import C
from makebp.specs.rest_d import D2
from makebp.specs.rest_e import E

REST = build_rest(A + B + C + D2 + E)
