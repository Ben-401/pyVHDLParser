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
from pyVHDLParser.Token                     import LinebreakToken, CommentToken, MultiLineCommentToken, IndentationToken, SingleLineCommentToken
from pyVHDLParser.Token.Parser              import StringToken, SpaceToken
from pyVHDLParser.Token.Keywords            import EntityKeyword, IsKeyword, EndKeyword, GenericKeyword, PortKeyword, UseKeyword, BeginKeyword
from pyVHDLParser.Token.Keywords            import BoundaryToken, IdentifierToken
from pyVHDLParser.Token.Keywords            import ConstantKeyword#, SharedKeyword, ProcedureKeyword, FunctionKeyword, PureKeyword, ImpureKeyword
from pyVHDLParser.Blocks                    import TokenParserException, Block, CommentBlock
from pyVHDLParser.Blocks.Common             import LinebreakBlock, IndentationBlock, WhitespaceBlock
from pyVHDLParser.Blocks.Generic            import BeginBlock as BeginBlockBase, EndBlock as EndBlockBase
from pyVHDLParser.Blocks.List               import GenericList, PortList
from pyVHDLParser.Blocks.Reference          import Use
from pyVHDLParser.Blocks.ObjectDeclaration  import Constant#, SharedVariable
# from pyVHDLParser.Blocks.Sequential         import Procedure, Function
from pyVHDLParser.Blocks.Parser             import TokenToBlockParser

# Type alias for type hinting
ParserState = TokenToBlockParser.TokenParserState


class NameBlock(Block):
	@classmethod
	def stateEntityKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       LinebreakBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected whitespace after keyword ENTITY.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			parserState.NewToken =      IdentifierToken(token)
			parserState.NextState =     cls.stateEntityName
			return
		elif isinstance(token, LinebreakToken):
			if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
				parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				_ =                       LinebreakBlock(parserState.NewBlock, token)
			else:
				parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker =   None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =      CommentBlock(parserState.LastBlock, token)
			parserState.TokenMarker =   None
			return
		elif (isinstance(token, IndentationToken) and isinstance(token.PreviousToken, (LinebreakToken, SingleLineCommentToken))):
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise TokenParserException("Expected entity name (identifier).", token)

	@classmethod
	def stateEntityName(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace2
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       LinebreakBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace2
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace2
			return

		raise TokenParserException("Expected whitespace after entity name.", token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, StringToken) and (token <= "is")):
			parserState.NewToken =      IsKeyword(token)
			parserState.NewBlock =      cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.TokenMarker =   None
			parserState.NextState =     cls.stateDeclarativeRegion
			return
		elif isinstance(token, LinebreakToken):
			if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
				parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				_ =                       LinebreakBlock(parserState.NewBlock, token)
			else:
				parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker =   None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =      cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                         CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker =   None
			return
		elif (isinstance(token, IndentationToken) and isinstance(token.PreviousToken, (LinebreakToken, SingleLineCommentToken))):
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken =      BoundaryToken(token)
			parserState.NewBlock =      WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker =   None
			return

		raise TokenParserException("Expected keyword IS after entity name.", token)

	@classmethod
	def stateDeclarativeRegion(cls, parserState: ParserState):
		keywords = {
			# Keyword     Transition
			UseKeyword:       Use.UseBlock.stateUseKeyword,
			GenericKeyword:   GenericList.OpenBlock.stateGenericKeyword,
			PortKeyword:      PortList.OpenBlock.statePortKeyword,
			ConstantKeyword:  Constant.ConstantBlock.stateConstantKeyword,
			# SharedKeyword:    SharedVariable.SharedVariableBlock.stateSharedKeyword,
			# ProcedureKeyword: Procedure.NameBlock.stateProcesdureKeyword,
			# FunctionKeyword:  Function.NameBlock.stateFunctionKeyword,
			# PureKeyword:      Function.NameBlock.statePureKeyword,
			# ImpureKeyword:    Function.NameBlock.stateImpureKeyword
		}

		token = parserState.Token
		if isinstance(token, SpaceToken):
			blockType =                 IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =      blockType(parserState.LastBlock, token)
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =      LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker =   None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =      CommentBlock(parserState.LastBlock, token)
			parserState.TokenMarker =   None
			return
		elif isinstance(token, StringToken):
			tokenValue = token.Value.lower()

			for keyword in keywords:
				if (tokenValue == keyword.__KEYWORD__):
					newToken =                keyword(token)
					parserState.PushState =   keywords[keyword]
					parserState.NewToken =    newToken
					parserState.TokenMarker = newToken
					return

			if (tokenValue == "begin"):
				parserState.NewToken =  BeginKeyword(token)
				parserState.NextState = BeginBlock.stateBeginKeyword
				return
			elif (tokenValue == "end"):
				parserState.NewToken =  EndKeyword(token)
				parserState.NextState = EndBlock.stateEndKeyword
				return

		raise TokenParserException(
			"Expected one of these keywords: END, {keywords}. Found: '{tokenValue}'.".format(
				keywords=", ".join(
					[kw.__KEYWORD__.upper() for kw in keywords]
				),
				tokenValue=token.Value
			), token)


class EndBlock(EndBlockBase):
	KEYWORD =             EntityKeyword
	KEYWORD_IS_OPTIONAL = True
	EXPECTED_NAME =       KEYWORD.__KEYWORD__


class BeginBlock(BeginBlockBase):
	END_BLOCK = EndBlock
