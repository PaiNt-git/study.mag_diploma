#!/usr/bin/env bash

# https://www.svgrepo.com/vectors/

# изменение размера
if [[ `command -v rsvg-convert` == '' ]]; then
    sudo apt install librsvg2-bin
fi

# сжатие
if [[ `command -v npm` == '' ]]; then
    sudo apt install npm
    npm install svgo
fi

if [[ `command -v svgo` == '' ]]; then
    PATH=$(npm bin):$PATH
fi

width="$1"
height="$2"

if [[ "${width}" == '' || "${height}" == '' ]]; then
    echo 'Укажи длину и ширину в передаваемых параметрах!'
    exit 1
fi

main_dir=`pwd`
dest_dir="${main_dir}/resized_svg/"
mkdir -p "${dest_dir}"

for input_file in *.svg; do
    output_file="${dest_dir}/`basename "${input_file}"`"

    src_width=`identify -format '%w' "${input_file}"`
    src_height=`identify -format '%h' "${input_file}"`
    if [[ "${src_width}" == "${width}" && "${src_height}" == "${width}" ]]; then
        echo -e "\ncp mode for `basename ${input_file}`"
        cp "${input_file}" "${output_file}"
    else
        if [[ -f "${output_file}" ]]; then rm "${output_file}"; fi
        comments=$(grep -o "<!--.*-->" "${input_file}")
        rsvg-convert "${input_file}" -w "${width}" -h "${height}" -f svg -o "${output_file}"
    fi
    svgo "${output_file}"
done

