"""Scenario specs compiled into blueprint folders."""

from makebp.specs.catalog_rest import REST
from makebp.specs.flagship import FLAGSHIP
from makebp.specs.flagship_b import FLAGSHIP_B
from makebp.specs.flagship_c import FLAGSHIP_C
from makebp.specs.flagship_d import FLAGSHIP_D

SPECS = FLAGSHIP + FLAGSHIP_B + FLAGSHIP_C + FLAGSHIP_D + REST
