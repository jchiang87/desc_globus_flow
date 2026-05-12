import lsst.daf.butler as daf_butler
from lsst.daf.butler.script import queryDatasetTypes


def create_export_yaml(repo, run_collection, export_file, dest_dir='.'):
    butler = daf_butler.Butler(repo, collections=[run_collection])
    dstypes = queryDatasetTypes(repo, False, ..., [run_collection])
    refs = set()
    with butler.export(directory=dest_dir, filename=export_file,
                       transfer=None) as exporter:
        for dstype in dstypes["name"]:
            my_refs = set(butler.registry.queryDatasets(dstype))
            refs = refs.union(my_refs)
        refs = list(refs)
        exporter.saveCollection(run_collection)
        exporter.saveDatasets(refs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=str, help="Data repository")
    parser.add_argument("run_collection", type=str, help="RUN collection")
    parser.add_argument("export_file", type=str, help="Export file name")

    args = parser.parse_args()
    create_export_yaml(args.repo, args.run_collection, args.export_file)
