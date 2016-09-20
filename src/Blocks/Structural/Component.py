from src.Blocks.Comment   import SingleLineCommentBlock, MultiLineCommentBlock
from src.Blocks.Common    import Block, EmptyLineBlock, IndentationBlock
from src.Blocks.List      import GenericList, PortList
from src.Token.Parser import CharacterToken, SpaceToken, StringToken, ParserException
from src.Token.Keywords import BoundaryToken, LinebreakToken, IdentifierToken, IndentationToken, EndToken
from src.Token.Keywords import ComponentKeyword, IsKeyword, EndKeyword, GenericKeyword, PortKeyword


class NameBlock(Block):
	def RegisterStates(self):
		return [
			self.stateComponentKeyword,
			self.stateWhitespace1,
			self.stateComponentName,
			self.stateWhitespace2,
			self.stateDeclarativeRegion
		]

	@classmethod
	def stateComponentKeyword(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword "
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   EmptyLineBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NextState =     cls.stateWhitespace1
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateWhitespace1(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected component name (identifier)."
		if isinstance(token, CharacterToken):
			if (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, StringToken):
			parserState.NewToken =      IdentifierToken(token)
			parserState.NextState =     cls.stateComponentName
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateComponentName(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword "
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   EmptyLineBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NextState =     cls.stateWhitespace2
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateWhitespace2(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected keyword IS after component name."
		if isinstance(token, CharacterToken):
			if (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif (isinstance(token, StringToken) and (token <= "is")):
			parserState.NewToken =      IsKeyword(token)
			parserState.NewBlock =      NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.NextState =     cls.stateDeclarativeRegion
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateDeclarativeRegion(cls, parserState):
		errorMessage = "Expected one of these keywords: generic, port, begin, end."
		token = parserState.Token
		if isinstance(parserState.Token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    EmptyLineBlock(parserState.LastBlock, parserState.NewToken, endToken=parserState.NewToken)
				parserState.TokenMarker = parserState.NewToken
				return
			elif (token == "-"):
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =      IndentationToken(token)
			parserState.NewBlock =      IndentationBlock(parserState.LastBlock, parserState.NewToken, endToken=parserState.NewToken)
			return
		elif isinstance(token, StringToken):
			keyword = token.Value.lower()
			if (keyword == "generic"):
				newToken =              GenericKeyword(token)
				parserState.PushState = GenericList.OpenBlock.stateGenericKeyword
			elif (keyword == "port"):
				newToken =              PortKeyword(token)
				parserState.PushState = PortList.OpenBlock.statePortKeyword
			elif (keyword == "end"):
				newToken =              EndKeyword(token)
				parserState.NextState = EndBlock.stateEndKeyword
			else:
				raise ParserException(errorMessage, token)

			parserState.NewToken =      newToken
			parserState.TokenMarker =   newToken
			return

		raise ParserException(errorMessage, token)


class EndBlock(Block):
	def RegisterStates(self):
		return [
			self.stateEndKeyword,
			self.stateWhitespace1,
			self.stateComponentKeyword,
			self.stateWhitespace2,
			self.stateComponentName,
			self.stateWhitespace3
		]

	@classmethod
	def stateEndKeyword(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   EmptyLineBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NextState =     cls.stateWhitespace1
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateWhitespace1(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';', COMPONENT keyword or component name."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, StringToken):
			if (token <= "component"):
				parserState.NewToken =    ComponentKeyword(token)
				parserState.NextState =   cls.stateComponentKeyword
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.NextState =   cls.stateComponentName
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateComponentKeyword(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   EmptyLineBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NextState =     cls.stateWhitespace2
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateWhitespace2(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';' or component name."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, StringToken):
			parserState.NewToken =    IdentifierToken(token)
			parserState.NextState =   cls.stateComponentName
			return

		raise ParserException(errorMessage, token)

	@classmethod
	def stateComponentName(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   EmptyLineBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NextState =     cls.stateWhitespace3
			return

	@classmethod
	def stateWhitespace3(cls, parserState):
		token = parserState.Token
		errorMessage = "Expected ';'."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return

		raise ParserException(errorMessage, token)

# class Component(BlockGroup):
# class NameBlock(Block):
# 	def RegisterStates(self):
# 		return [
# 			self.stateComponentKeyword,
# 			self.stateWhitespace1,
# 			self.stateComponentName,
# 			self.stateWhitespace2,
# 			self.stateDeclarativeRegion
# 		]
#
# 	@classmethod
# 	def stateComponentKeyword(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected whitespace after keyword COMPONENT."
# 		if isinstance(token, CharacterToken):
# 			if (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   EmptyLineBlock.stateLinebreak
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NewToken =      BoundaryToken(token)
# 			parserState.NextState =     cls.stateWhitespace1
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateWhitespace1(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected component name (identifier)."
# 		if isinstance(token, CharacterToken):
# 			if (token == "-"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, StringToken):
# 			parserState.NewToken =      IdentifierToken(token)
# 			parserState.NextState =     cls.stateComponentName
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateComponentName(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected whitespace after keyword COMPONENT."
# 		if isinstance(token, CharacterToken):
# 			if (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   EmptyLineBlock.stateLinebreak
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NextState =     cls.stateWhitespace2
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateWhitespace2(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected keyword IS after component name."
# 		if isinstance(token, CharacterToken):
# 			if (token == "-"):
# 				parserState.NewBlock =    LibraryBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    LibraryBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif (isinstance(token, StringToken) and (token <= "is")):
# 			parserState.NewToken =      IsKeyword(token)
# 			parserState.NewBlock =      Component.NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 			parserState.NextState =     cls.stateDeclarativeRegion
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateDeclarativeRegion(cls, parserState):
# 		errorMessage = "Expected one of these keywords: generic, port, begin, end."
# 		token = parserState.Token
# 		if isinstance(parserState.Token, CharacterToken):
# 			if (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    EmptyLineBlock(parserState.LastBlock, parserState.NewToken, endToken=parserState.NewToken)
# 				parserState.TokenMarker = parserState.NewToken
# 				return
# 			elif (token == "-"):
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NewToken =      IndentationToken(token)
# 			parserState.NewBlock =      IndentationBlock(parserState.LastBlock, parserState.NewToken, endToken=parserState.NewToken)
# 			return
# 		elif isinstance(token, StringToken):
# 			keyword = token.Value.lower()
# 			if (keyword == "generic"):
# 				newToken =              GenericKeyword(token)
# 				parserState.PushState = GenericList.OpenBlock.stateGenericKeyword
# 			elif (keyword == "port"):
# 				newToken =              PortKeyword(token)
# 				parserState.PushState = PortList.OpenBlock.statePortKeyword
# 			elif (keyword == "end"):
# 				newToken =              EndKeyword(token)
# 				parserState.NextState = Component.EndBlock.stateEndKeyword
# 			elif (keyword == "begin"):
# 				parserState.NewToken =  BeginKeyword(token)
# 				parserState.NewBlock =  Component.BeginBlock(parserState.LastBlock, parserState.NewToken, endToken=parserState.NewToken)
# 				parserState.NextState = Component.BeginBlock.stateBeginKeyword
# 				return
# 			else:
# 				raise ParserException(errorMessage, token)
#
# 			parserState.NewToken =      newToken
# 			parserState.TokenMarker =   newToken
# 			return
#
# 		raise ParserException(errorMessage, token)
#
#
# class EndBlock(Block):
# 	def RegisterStates(self):
# 		return [
# 			self.stateEndKeyword,
# 			self.stateWhitespace1,
# 			self.stateComponentKeyword,
# 			self.stateWhitespace2,
# 			self.stateComponentName,
# 			self.stateWhitespace3
# 		]
#
# 	@classmethod
# 	def stateEndKeyword(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';' or whitespace."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   EmptyLineBlock.stateLinebreak
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NewToken =      BoundaryToken(token)
# 			parserState.NextState =     cls.stateWhitespace1
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateWhitespace1(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';', COMPONENT keyword or component name."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    LibraryBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    LibraryBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, StringToken):
# 			if (token <= "component"):
# 				parserState.NewToken =    ComponentKeyword(token)
# 				parserState.NextState =   cls.stateComponentKeyword
# 			else:
# 				parserState.NewToken =    IdentifierToken(token)
# 				parserState.NextState =   cls.stateComponentName
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateComponentKeyword(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';' or whitespace."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   EmptyLineBlock.stateLinebreak
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace1
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NewToken =      BoundaryToken(token)
# 			parserState.NextState =     cls.stateWhitespace2
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateWhitespace2(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';' or component name."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, StringToken):
# 			parserState.NewToken =    IdentifierToken(token)
# 			parserState.NextState =   cls.stateComponentName
# 			return
#
# 		raise ParserException(errorMessage, token)
#
# 	@classmethod
# 	def stateComponentName(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';' or whitespace."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "\n"):
# 				parserState.NewToken =    LinebreakToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   EmptyLineBlock.stateLinebreak
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.NextState =   cls.stateWhitespace2
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 		elif isinstance(token, SpaceToken):
# 			parserState.NextState =     cls.stateWhitespace3
# 			return
#
# 	@classmethod
# 	def stateWhitespace3(cls, parserState):
# 		token = parserState.Token
# 		errorMessage = "Expected ';'."
# 		if isinstance(token, CharacterToken):
# 			if (token == ";"):
# 				parserState.NewToken =    EndToken(token)
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
# 				parserState.Pop()
# 				return
# 			elif (token == "-"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
# 			elif (token == "/"):
# 				parserState.NewBlock =    Component.EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
# 				parserState.TokenMarker = None
# 				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
# 				parserState.TokenMarker = token
# 				return
#
# 		raise ParserException(errorMessage, token)
