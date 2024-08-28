import argparse
import stt_selector as stt

parser = argparse.ArgumentParser(prog="STT", description="STT main script")
parser.add_argument("type", type=str,
                    help="The way of running the software: direct_rpi, sample_rpi, sample_stereo.")
parser.add_argument("catalog", type=int,
                    help="The degree of catalog separation in the algorithm: 5, 10, 15.")
parser.add_argument("-exp", "--exptime", type=int,
                    help="Exposure time (in ms) of the grabbed picture (in direct mode).", default=800)
parser.add_argument("-n", "--npic", type=int,
                    help="The number of the picture to analyze (in sample mode).", default=1)
args = parser.parse_args()
stt_type = args.type
cat_division = args.catalog
n_pic = args.npic
exp_time = args.exptime

if cat_division not in (5, 10, 15):
    parser.error("Please introduce a valid catalog division: 5/10/15")

if stt_type == "direct_rpi":
    stt.solve_lis_grab_img(cat_division, exp_time)
elif stt_type == "sample_rpi":
    stt.solve_lis_sample_rpi(cat_division, n_pic)
elif stt_type == "sample_stereo":
    stt.solve_lis_sample_stereo(cat_division, n_pic)
else:
    raise NameError("---> ERROR: Please introduce a valid option to use this STT software (see the Documentation)!")
