# Data and checkpoint provenance

The three cached sparse graph files are copied from the supplied Fly experiments:
`graph_211.npz` from the Gate 3 archive, `graph_223.npz` and `graph_239.npz` from
Gate 2F. The active model uses the first 256 nodes after sparse normalization.
Teacher assignment 7101 uses graph 211; recipients 7102/7103 use 223/239.

The earlier source record identifies FlyWire v783 connectivity, Eon repository
commit `a3db62f9436074e485c0278290c2164ed6150808`, and original table blob IDs.
That record is included verbatim in `upstream/connectome_source.json`; the
original notice is `upstream/NOTICE.md`. These are provenance supplied with the
research package, not a fresh upstream data audit.

Teacher checkpoints and packets originate in Gates 2C/2F. The release verifies
that each included teacher and each 97-byte packet expresses the canonical
24-state convention. That verifies current artifact behavior, not the historical
training trajectory that produced every checkpoint. Fresh teacher training is
available as a separate command and must receive its own run record.

All runtime resources are listed in `src/iap/assets/MANIFEST.json` with byte
counts and SHA-256 values. Whole input archives are listed in
`evidence/SOURCES.json`. Selected Doom live evidence carries a separate
`evidence/doom_basic_live/SOURCE.json` provenance record.

Before public redistribution, verify exact code/data/checkpoint rights and
attribution. The upstream licenses in this repository are retained notices,
not a substitute for that review. No Doom engine, game asset, dependency wheel,
font, user credentials, or Python virtual environment is included.
