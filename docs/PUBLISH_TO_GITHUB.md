# Publish the repository

This package is a local GitHub-ready source tree. Generating it did not create a
remote repository, upload data, reserve a package name, or publish a release.

Review `LICENSE`, `THIRD_PARTY_NOTICES.md`, `docs/DATA_PROVENANCE.md` and the
publication checklist before making the repository public. No broad open-source
license has been chosen without the maintainer's decision.

Initialize a local repository from the extracted root:

```bash
git init -b main
git add .
git commit -m "IAP v1.0 research release"
git tag -a v1.0.0 -m "IAP v1.0 research implementation"
```

Create an empty remote repository under the desired account, then add the real
remote URL using GitHub's instructions and push the main branch and tag. The
suggested repository name is `inter-agent-protocol`. No account or URL is assumed
by this package. Add the actual URL to `CITATION.cff` and `pyproject.toml` afterward.

The supplied workflow runs software checks on Linux and Windows. There is no
automatic publication to PyPI or automatic remote release creation. Those would
require explicit credentials/permissions and a licensing decision.

Include the full repository ZIP as a release artifact for archives/evidence.
The built wheel is a smaller runnable distribution and does not contain the
full historical experiment record. Do not substitute it for that record in a
paper's artifact-availability statement.
