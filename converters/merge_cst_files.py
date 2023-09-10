import glob

def merge_cst_files():
    file_pattern = "*.cst"
    cst_files = glob.glob(file_pattern)
    cst_content = []

    for cst_file in cst_files:
        with open(cst_file, "r") as f:
            cst_content.append(f.read())
    merged_content = "\n".join(cst_content)

    return merged_content