#!/usr/bin/env sh

# super hacky way of bundling our dependencies for distribution; just extract
# the wheels into a subdirectory.
# whatever it works for now

deps_dir=extern

mkdir -p "$deps_dir"
pip wheel --wheel-dir "$deps_dir" -r requirements.txt
for wheel in "$deps_dir"/*.whl; do
    unzip -qo "$wheel" -x "*.dist-info/*" -d "$deps_dir"
    rm "$wheel"
done

orig_dir="$PWD"
orig_name=$(basename "$orig_dir")
cd ".."
zip -r "$orig_dir/$orig_name.zip" "$orig_name" -x "*__pycache__*" "*.git*" "$orig_name/make_zip.sh" "$orig_name/$orig_name.zip"
cd "$orig_dir"
