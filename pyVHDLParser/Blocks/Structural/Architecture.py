# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python functions:   A streaming VHDL parser
#
# Description:
# ------------------------------------
#		TODO:
#
# License:
# ==============================================================================
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
# load dependencies
from pyVHDLParser.Token.Keywords       import BoundaryToken, LinebreakToken, IdentifierToken, IndentationToken, EndToken
from pyVHDLParser.Token.Keywords       import SignalKeyword, ConstantKeyword, VariableKeyword, SharedKeyword, ProcessKeyword, AssertKeyword
from pyVHDLParser.Token.Keywords       import IsKeyword, EndKeyword, ArchitectureKeyword, BeginKeyword, OfKeyword
from pyVHDLParser.Token.Parser         import CharacterToken, SpaceToken, StringToken
from pyVHDLParser.Blocks.Parser        import TokenToBlockParser
from pyVHDLParser.Blocks.Exception     import BlockParserException
from pyVHDLParser.Blocks.Base          import Block
from pyVHDLParser.Blocks.Common        import LinebreakBlock, IndentationBlock, WhitespaceBlock
from pyVHDLParser.Blocks.Comment       import SingleLineCommentBlock, MultiLineCommentBlock
from pyVHDLParser.Blocks.Reporting     import Assert
from pyVHDLParser.Blocks.Sequential    import Process
from pyVHDLParser.Blocks.ObjectDeclaration import Constant, Signal, Variable, SharedVariable

# Type alias for type hinting
ParserState = TokenToBlockParser.TokenParserState


class NameBlock(Block):
	def RegisterStates(self):
		return [
			self.stateArchitectureKeyword,
			self.stateWhitespace1,
			self.stateArchitectureName,
			self.stateWhitespace2,
			self.stateEntityName,
			self.stateWhitespace3,
			self.stateDeclarativeRegion
		]

	@classmethod
	def stateArchitectureKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword "
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   LinebreakBlock.stateLinebreak
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

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected architecture name (identifier)."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
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
			parserState.NextState =     cls.stateArchitectureName
			return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateArchitectureName(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword "
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   LinebreakBlock.stateLinebreak
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

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected keyword IS after architecture name."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
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
		elif (isinstance(token, StringToken) and (token <= "of")):
			parserState.NewToken =      OfKeyword(token)
			parserState.NextState =     cls.stateOfKeyword
			return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateOfKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword OF."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NextState =     cls.stateWhitespace3
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace3(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected entity name (identifier)."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
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
			parserState.NextState =     cls.stateEntityName
			return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateEntityName(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after entity name."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace4
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace4
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace4
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NextState =     cls.stateWhitespace4
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace4(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected keyword IS after entity name."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  NameBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
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
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateDeclarativeRegion(cls, parserState: ParserState):
		errorMessage = "Expected one of these keywords: signal, constant, variable, shared, begin."
		token = parserState.Token
		if isinstance(parserState.Token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, parserState.NewToken)
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
			parserState.NewBlock =      IndentationBlock(parserState.LastBlock, parserState.NewToken)
			return
		elif isinstance(token, StringToken):
			keyword = token.Value.lower()
			if (keyword == "signal"):
				newToken =              SignalKeyword(token)
				parserState.PushState = Signal.SignalBlock.stateSignalKeyword
			elif (keyword == "constant"):
				newToken =              ConstantKeyword(token)
				parserState.PushState = Constant.ConstantBlock.stateConstantKeyword
			elif (keyword == "variable"):
				newToken =              VariableKeyword(token)
				parserState.PushState = Variable.VariableBlock.stateVariableKeyword
			elif (keyword == "shared"):
				newToken =              SharedKeyword(token)
				parserState.PushState = SharedVariable.SharedVariableBlock.stateSharedKeyword
			# elif (keyword == "end"):
			# 	newToken =              EndKeyword(token)
			# 	parserState.NextState = EndBlock.stateEndKeyword
			elif (keyword == "begin"):
				parserState.NewToken =  BeginKeyword(token)
				parserState.NewBlock =  BeginBlock(parserState.LastBlock, parserState.NewToken)
				parserState.NextState = BeginBlock.stateBeginKeyword
				return
			else:
				raise BlockParserException(errorMessage, token)

			parserState.NewToken =      newToken
			parserState.TokenMarker =   newToken
			return

		raise BlockParserException(errorMessage, token)

class BeginBlock(Block):
	def RegisterStates(self):
		return [
			self.stateBeginKeyword
		]

	@classmethod
	def stateBeginKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected label or one of these keywords: assert, process."
		if isinstance(token, CharacterToken):
			if (token == "\n"):
				parserState.NewToken =      LinebreakToken(token)
				parserState.NewBlock =      LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker =   None
				return
			elif (token == "-"):
				parserState.PushState =     SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker =   token
				return
			elif (token == "/"):
				parserState.PushState =     MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker =   token
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =        IndentationToken(token)
			parserState.NewBlock =        IndentationBlock(parserState.LastBlock, parserState.NewToken)
			return
		elif isinstance(token, StringToken):
			keyword = token.Value.lower()
			if (keyword == "process"):
				newToken =                  ProcessKeyword(token)
				parserState.PushState =     Process.OpenBlock.stateProcessKeyword
			elif (keyword == "assert"):
				newToken =                  AssertKeyword(token)
				parserState.PushState =     Assert.AssertBlock.stateAssertKeyword
			elif (keyword == "end"):
				newToken =                  EndKeyword(token)
				parserState.NextState =     EndBlock.stateEndKeyword
			else:
				raise BlockParserException(errorMessage, token)

			parserState.NewToken =        newToken
			parserState.TokenMarker =     newToken
			return

		raise BlockParserException(errorMessage, token)

class EndBlock(Block):
	def RegisterStates(self):
		return [
			self.stateEndKeyword,
			self.stateWhitespace1,
			self.stateArchitectureKeyword,
			self.stateWhitespace2,
			self.stateArchitectureName,
			self.stateWhitespace3
		]

	@classmethod
	def stateEndKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace1
				parserState.PushState =   LinebreakBlock.stateLinebreak
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

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';', ARCHITECTURE keyword or architecture name."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
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
			if (token <= "architecture"):
				parserState.NewToken =    ArchitectureKeyword(token)
				parserState.NextState =   cls.stateArchitectureKeyword
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.NextState =   cls.stateArchitectureName
			return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateArchitectureKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace2
				parserState.PushState =   LinebreakBlock.stateLinebreak
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
			parserState.NewToken =      BoundaryToken(token)
			parserState.NextState =     cls.stateWhitespace2
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';' or architecture name."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
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
			parserState.NextState =   cls.stateArchitectureName
			return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)

	@classmethod
	def stateArchitectureName(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';' or whitespace."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.NewToken =    LinebreakToken(token)
				_ =                       LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   LinebreakBlock.stateLinebreak
				return
			elif (token == "-"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   SingleLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
			elif (token == "/"):
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				parserState.TokenMarker = None
				parserState.NextState =   cls.stateWhitespace3
				parserState.PushState =   MultiLineCommentBlock.statePossibleCommentStart
				parserState.TokenMarker = token
				return
		elif isinstance(token, SpaceToken):
			parserState.NextState =     cls.stateWhitespace3
			return

	@classmethod
	def stateWhitespace3(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected ';'."
		if isinstance(token, CharacterToken):
			if (token == ";"):
				parserState.NewToken =    EndToken(token)
				parserState.NewBlock =    EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.Pop()
				return
			elif (token == "\n"):
				parserState.NewToken =    LinebreakToken(token)
				if (not isinstance(parserState.LastBlock, MultiLineCommentBlock)):
					parserState.NewBlock =  EndBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken, multiPart=True)
					_ =                     LinebreakBlock(parserState.NewBlock, parserState.NewToken)
				else:
					parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.PushState =   LinebreakBlock.stateLinebreak
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
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise BlockParserException(errorMessage, token)
