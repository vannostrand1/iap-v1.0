# Third-party and research-asset notices

The supplied research archives identify graph resources as derived from FlyWire
v783 connectivity distributed in the Eon fly-brain repository. The retained
`upstream/connectome_source.json` records commit and original table blob IDs.
This release preserves that provenance assertion; it has not independently
re-downloaded or re-derived the full upstream dataset.

`upstream/NOTICE.md`, `upstream/EON_LICENSE`, and
`upstream/DENDRITRON_LICENSE` are preserved verbatim from the prior Gate 3
package. The historical notice describes more components than this release
uses: IAP v1.0 does not include the Eon spiking simulator, the Dendritron Doom
scaffold, the ViZDoom engine, or game assets. Retaining a notice is not a claim
that every listed component is used, nor a grant to relicense its data.

The active `InternalFly` is adapted from the supplied `internal_model.py`, a
normalized leaky tanh rate circuit. Its source ancestry and graph resources
must be reviewed before selecting a repository-wide public license.

NumPy, SciPy, PyTorch, pytest and build tools are installed dependencies; they
are not bundled as executables or relicensed. The original IAP software,
third-party graph assets, generated teacher checkpoints, archived experiments,
and their respective permissions need separate consideration. No broad license
has been silently assigned to all of them. See `LICENSE` and
`docs/DATA_PROVENANCE.md`.
