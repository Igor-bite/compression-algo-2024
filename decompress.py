import sys
import coder, compression_params

MODEL_ORDER = 3

def main(args):
	if len(args) != 2:
		sys.exit("How to use: python decompress.py input_file output_file")
	inputfile  = args[0]
	outputfile = args[1]
 
	with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
		bitin = coder.BitInputStream(inp)
		decompress(bitin, out)


def decompress(bitin, out):
	dec = coder.ArithmeticDecoder(32, bitin)
	model = compression_params.CompressionParams(MODEL_ORDER, 257, 256)
	history = []

	print("Decompressing...\n")
	
	while True:
		symbol = decode_symbol(dec, model, history)
		if symbol == 256:  
			break
		out.write(bytes((symbol,)))
		model.increment_contexts(history, symbol)
		
		if model.model_order >= 1:
			if len(history) == model.model_order:
				history.pop()
			history.insert(0, symbol)


def decode_symbol(dec, model, history):
	for order in reversed(range(len(history) + 1)):
		ctx = model.root_context
		for sym in history[ : order]:
			assert ctx.subcontexts is not None
			ctx = ctx.subcontexts[sym]
			if ctx is None:
				break
		else:  
			symbol = dec.read(ctx.frequencies)
			if symbol < 256:
				return symbol
	return dec.read(model.order_minus1_freqs)


if __name__ == "__main__":
	main(sys.argv[1 : ])
