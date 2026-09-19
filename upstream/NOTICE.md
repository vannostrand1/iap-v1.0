# Sources and scope

The cached connectivity derives from the real FlyWire v783 data distributed
in [Eon's fly-brain repository](https://github.com/eonsystemspbc/fly-brain/tree/a3db62f9436074e485c0278290c2164ed6150808).
The exact commit, original table blob hashes, and source dimensions are in
`data/connectome_source.json`. Preserve original dataset terms and citations
for downstream research or redistribution. The package retains
`upstream/EON_LICENSE` and a source copy of `run_pytorch.py`.

`fly_core.py` is the unchanged earlier experimental adaptation of those
spiking equations, with artificial inputs/readouts and reduced induced graphs.
`lif_encoder.py` accelerates that adaptation; numerical equivalence is tested
on retained Poisson fixtures. `internal_model.py` is a separate normalized
tanh rate model and must not be labeled an exact Eon simulation.

The Gaussian-branch scaffold follows the previously examined
[Dendritron starter kit](https://github.com/MMVFIRM/dendritron-starter-kit/tree/ea3fa1209cbbca425cd378a6cd26602d4d563d53)
idea of fixed prototypes, sparse routing and learned values. This Doom
variant uses Double DQN and Adam rather than the earlier reward update.
`upstream/DENDRITRON_LICENSE` is retained. No transformer comparison is made.

[ViZDoom](https://github.com/Farama-Foundation/ViZDoom) and its packaged
Freedoom assets are installed as dependencies; their files and licenses are
not relicensed by this experiment. This ZIP contains no Doom game assets.

[Doomfly](https://github.com/nftechie/doomfly) was examined as related work at
commit `71ecf53d78eaffaf1a57ed7b0ccf5d458abc9f33`. Its full MaleCNS circuit and
internal plasticity work are distinct from this package. No Doomfly source
or learned weights were used here.
