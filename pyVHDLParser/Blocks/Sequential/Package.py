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
# Copyright 2007-2017 Patrick Lehmann - Dresden, Germany
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
from pyVHDLParser.Token.Parser              import CharacterToken, StringToken, SpaceToken
from pyVHDLParser.Token.Keywords            import PackageKeyword, IsKeyword, EndKeyword, LinebreakToken, BoundaryToken, IdentifierToken, \
	IndentationToken, GenericKeyword, ConstantKeyword, VariableKeyword, SharedKeyword, ProcessKeyword, FunctionKeyword, PureKeyword, ImpureKeyword, EndToken, \
	BodyKeyword
from pyVHDLParser.Blocks                    import TokenParserException, Block
from pyVHDLParser.Blocks.Common             import LinebreakBlock, IndentationBlock, WhitespaceBlock
from pyVHDLParser.Blocks.Comment            import SingleLineCommentBlock, MultiLineCommentBlock
from pyVHDLParser.Blocks.Generic            import EndBlock as EndBlockBase
from pyVHDLParser.Blocks.List               import GenericList
from pyVHDLParser.Blocks.ObjectDeclaration  import Constant, Variable, SharedVariable
from pyVHDLParser.Blocks.Sequential         import PackageBody, Procedure, Function
from pyVHDLParser.Blocks.Parser             import TokenToBlockParser

# Type alias for type hinting
ParserState = TokenToBlockParser.TokenParserState


class NameBlock(Block):
	@classmethod
	def statePackageKeyword(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected whitespace after keyword PACKAGE."
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

		raise TokenParserException(errorMessage, token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected package name (identifier)."
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
			if (token <= "body"):
				parserState.NewToken =    BodyKeyword(token)
				parserState.NextState =   PackageBody.NameBlock.stateBodyKeyword
				return
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.NextState =   cls.statePackageName
				return
		elif (isinstance(token, SpaceToken) and isinstance(parserState.LastBlock, MultiLineCommentBlock)):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise TokenParserException(errorMessage, token)

	@classmethod
	def statePackageName(cls, parserState: ParserState):
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

		raise TokenParserException(errorMessage, token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		errorMessage = "Expected keyword IS after package name."
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

		raise TokenParserException(errorMessage, token)

	@classmethod
	def stateDeclarativeRegion(cls, parserState: ParserState):
		errorMessage = "Expected one of these keywords: generic, port, begin, end."
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
			if (keyword == "generic"):
				newToken =              GenericKeyword(token)
				parserState.PushState = GenericList.OpenBlock.stateGenericKeyword
			elif (keyword == "constant"):
				newToken =              ConstantKeyword(token)
				parserState.PushState = Constant.ConstantBlock.stateConstantKeyword
			elif (keyword == "variable"):
				newToken =              VariableKeyword(token)
				parserState.PushState = Variable.VariableBlock.stateVariableKeyword
			elif (keyword == "shared"):
				newToken =              SharedKeyword(token)
				parserState.PushState = SharedVariable.SharedVariableBlock.stateSharedKeyword
			elif (keyword == "procedure"):
				newToken =              ProcessKeyword(token)
				parserState.PushState = Procedure.NameBlock.stateProcesdureKeyword
			elif (keyword == "function"):
				newToken =              FunctionKeyword(token)
				parserState.PushState = Function.NameBlock.stateFunctionKeyword
			elif (keyword == "pure"):
				newToken =              PureKeyword(token)
				parserState.PushState = Function.NameBlock.statePureKeyword
			elif (keyword == "impure"):
				newToken =              ImpureKeyword(token)
				parserState.PushState = Function.NameBlock.stateImpureKeyword
			elif (keyword == "end"):
				newToken =              EndKeyword(token)
				parserState.NextState = EndBlock.stateEndKeyword
			else:
				raise TokenParserException(errorMessage, token)

			parserState.NewToken =      newToken
			parserState.TokenMarker =   newToken
			return

		raise TokenParserException(errorMessage, token)

class EndBlock(EndBlockBase):
	KEYWORD =             PackageKeyword
	KEYWORD_IS_OPTIONAL = True
	EXPECTED_NAME =       KEYWORD.__KEYWORD__
