# Security and execution boundaries

This is local research software, not a sandbox for untrusted models or data.
Do not load arbitrary `.pt` files. Included teacher assets are checked against a
manifest before restricted `torch.load(..., weights_only=True)` loading.
Student loading also uses restricted loading and a benchmark-specific size
limit. These precautions do not make an untrusted checkpoint risk-free.

The compact capsule parser accepts fixed-size numerical formats, validates
headers/scales, rejects excessive lengths, and checks framed payload hashes.
SHA-256 establishes consistency, not sender authentication or scientific truth.
A malicious but well-formed policy may still teach harmful or wrong behavior.

The learner API never receives benchmark truth. The calibration adapter is
explicitly privileged and its queries are counted. This is a software boundary,
not protection against a malicious process with access to experiment files.

The runner has no network calls or credentials. The optional setup script uses
pip to download declared dependencies into a local virtual environment. It
does not install Python system-wide or upload results. No remote repository is
created automatically. Review logs before publishing, because package-manager
messages can include local filesystem paths.

For a security issue, contact the repository maintainer privately through the
hosting platform when a public repository/contact channel is established.
Do not put credentials or private data in an issue or result archive.
