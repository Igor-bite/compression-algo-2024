from io import BufferedReader
import contextlib, sys
import coder, compression_params
from pathlib import Path
from entropy_calc import calc_entropy

MODEL_ORDER = 3

def main(args):
	if len(args) != 2:
		sys.exit("How to use: python compress.py input_file output_file")
	inputfile  = args[0]
	outputfile = args[1]

	print("Compressing...\n")

	with open(inputfile, "rb") as inp, \
			contextlib.closing(coder.BitOutputStream(open(outputfile, "wb"))) as bitout:
		
		compress(inp, bitout, MODEL_ORDER)
		print_stats(inputfile, outputfile)


def print_stats(inputfile, outputfile):
	input_size = Path(inputfile).stat().st_size
	output_size = Path(outputfile).stat().st_size
	bits_by_symbol = output_size * 8 / input_size
	(h_x, h_x_x, h_x_xx) = calc_entropy(inputfile)
	print(f"============  {inputfile} --> {outputfile}  ============")
	print(f"Size: {input_size} --> {output_size}")
	print(f"{round(bits_by_symbol, 2)} bits for symbol")
	print(f"H(X) = {round(h_x, 2)}")
	print(f"H(X|X) = {round(h_x_x, 2)}")
	print(f"H(X|XX) = {round(h_x_xx, 2)}")
		

def compress(inp: BufferedReader, bitout: coder.BitOutputStream, model_order: int = MODEL_ORDER):
	enc = coder.ArithmeticEncoder(32, bitout)
	model = compression_params.CompressionParams(model_order, 257, 256)
	history = []
	
	while True:
		symbol = inp.read(1)
		if len(symbol) == 0:
			break
		symbol = symbol[0]
		encode_symbol(model, history, symbol, enc)
		model.increment_contexts(history, symbol)
		
		# Обновление текущей истории
		if model.model_order >= 1:
			if len(history) == model.model_order:
				history.pop()
			history.insert(0, symbol)

	encode_symbol(model, history, 256, enc)  
	enc.finish()  


def encode_symbol(model, history, symbol, enc):
	for order in reversed(range(len(history) + 1)):
		ctx = model.root_context
		for sym in history[ : order]:
			assert ctx.subcontexts is not None
			ctx = ctx.subcontexts[sym]
			if ctx is None:
				break
		else:  
			if symbol != 256 and ctx.frequencies.get(symbol) > 0:
				enc.write(ctx.frequencies, symbol)
				return
			enc.write(ctx.frequencies, 256)	
	enc.write(model.order_minus1_freqs, symbol)


if __name__ == "__main__":
	main(sys.argv[1 : ])
