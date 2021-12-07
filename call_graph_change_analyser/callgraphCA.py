# %%
import argparse

# error messages
INVALID_FILETYPE_MSG = "Error: Invalid file format. %s must be a .txt file."
INVALID_PATH_MSG = "Error: Invalid file path/name. Path %s does not exist."


def main():
    # create parser object
    parser = argparse.ArgumentParser(
        description="A call graph and code evolution analytics tool.")

    # defining arguments for parser object
    parser.add_argument("-P", "--project", type=str, nargs=1,
                        metavar="project_name", default=None,
                        help="The name of the project, will be used to set the path of the resulting data.")

    parser.add_argument("-from_tag", "--from_tag", type=str, nargs=1,
                        metavar="git_tag", default=None,
                        help="Git repository tag.")

    parser.add_argument("-to_tag", "--to_tag", type=str, nargs=1,
                        metavar="git_tag", default=None,
                        help="Git repository tag.")

    parser.add_argument('-init_db', metavar="int_bool", type=int, nargs=1,
                        #dest='db_initialization',
                        help="Initialize the database = 1.")
    #parser.add_argument('--no-init_db', dest='feature', action='store_false')
    # parser.set_defaults(feature=True)

    # parse the arguments from standard input
    args = parser.parse_args()

    # calling functions depending on type of argument
    if args.init_db != None:
        init_db(args)


def init_db(args):
    print("init_db called")
    for arg in vars(args):
        print(arg, getattr(args, arg))
    # proj_paths
    #logging.info('Initialize the db.')
    #create_db_tables(proj_paths, drop=True)


# %%
if __name__ == "__main__":
    # calling the main function
    main()
