def build_report(file1_data, file2_data=None, duplicate=None, comparison=None):

    report = {
        "file1": file1_data
    }

    if file2_data:
        report["file2"] = file2_data

    if duplicate:
        report["duplicate"] = duplicate

    if comparison:
        report["comparison"] = comparison

    return report