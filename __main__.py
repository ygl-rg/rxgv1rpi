import sys


if __name__ == "__main__":
    args = sys.argv
    if args[1] == 'rxg_node':
        import go
        go.main(args[2])
    elif args[1] == 'rxg_gen_cfg':
        import gen_def_cfg
        gen_def_cfg.main(args[2])
    else:
        print("incorrect running mode")

