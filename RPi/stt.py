import argparse

parser = argparse.ArgumentParser(prog="STT", description="STT main script")
parser.add_argument("type", type=str, help="The way of running the software.")
parser.add_argument("catalog", type=int, help="The degree of catalog separation in the algorithm.")
args = parser.parse_args()
stt_type = args.type
cat_division = args.catalog

if cat_division not in (5, 10, 15):
    parser.error("Please introduce a valid catalog division: 5/10/15")

if stt_type == "real_rpi":
    print("a", cat_division)
elif stt_type == "sample_rpi":
    print("b", cat_division)
elif stt_type == "sample_stereo":
    print("c", cat_division)
else:
    raise NameError("---> ERROR: Please introduce a valid way to use this STT software")
