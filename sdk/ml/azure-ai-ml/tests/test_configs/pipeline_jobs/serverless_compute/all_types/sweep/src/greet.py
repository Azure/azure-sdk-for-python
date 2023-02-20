import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--whom", type=str, default="World")
    args = parser.parse_args()

    print(f"Hello {args.whom}!")
