# Release Process

This project uses GitHub Actions to build packages for Windows, macOS, and Linux.

## Build Without Releasing

Push to `main` or `develop`, or run the `Build and Release` workflow manually with an empty version input.

The workflow uploads build artifacts for each OS:

- `log-documentation-system-<version>-windows-installer.exe`
- `log-documentation-system-<version>-macos.dmg`
- `log-documentation-system-<version>-linux-amd64.deb`

## Create a Release

Update `VERSION`, commit it, then create and push a version tag:

```bash
git add VERSION
git commit -m "Bump version to 1.0.38"
git tag v1.0.38
git push origin main --tags
```

The release workflow will build all OS packages and publish them to a GitHub Release.

You can also run the workflow manually and enter a version such as `1.0.38`. That creates a release named `v1.0.38` from the selected branch.

## Version Source

For normal branch builds, package names use the value in `VERSION`.

For tag builds, the tag wins. For example, `v1.0.38` produces packages named with version `1.0.38`.
