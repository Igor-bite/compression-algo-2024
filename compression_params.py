import coder


class CompressionParams:
	def __init__(self, order, symbollimit, escapesymbol):
		if not ((order >= -1) and (0 <= escapesymbol < symbollimit)):
			raise ValueError()
		self.model_order = order
		self.symbol_limit = symbollimit
		self.escape_symbol = escapesymbol
		
		if order >= 0:
			self.root_context = CompressionParams.Context(symbollimit, order >= 1)
			self.root_context.frequencies.increment(escapesymbol)
		else:
			self.root_context = None
		self.order_minus1_freqs = coder.FlatFrequencyTable(symbollimit)
	
	
	def increment_contexts(self, history, symbol):
		if self.model_order == -1:
			return
		if not ((len(history) <= self.model_order) and (0 <= symbol < self.symbol_limit)):
			raise ValueError()
		
		ctx = self.root_context
		ctx.frequencies.increment(symbol)
		for (i, sym) in enumerate(history):
			subctxs = ctx.subcontexts
			assert subctxs is not None
			
			if subctxs[sym] is None:
				subctxs[sym] = CompressionParams.Context(self.symbol_limit, i + 1 < self.model_order)
				subctxs[sym].frequencies.increment(self.escape_symbol)
			ctx = subctxs[sym]
			ctx.frequencies.increment(symbol)
	
	
	class Context:	
		def __init__(self, symbols, hassubctx):
			self.frequencies = coder.SimpleFrequencyTable([0] * symbols)
			self.subcontexts = ([None] * symbols) if hassubctx else None
