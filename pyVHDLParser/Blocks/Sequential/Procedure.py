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
from pyVHDLParser.Token                     import SpaceToken, LinebreakToken, CommentToken, CharacterToken, IndentationToken, MultiLineCommentToken
from pyVHDLParser.Token.Keywords import StringToken, BoundaryToken, IdentifierToken, GenericKeyword, ParameterKeyword, ProcedureKeyword, EndKeyword, \
	ImpureKeyword, PureKeyword
from pyVHDLParser.Token.Keywords            import UseKeyword, ConstantKeyword, VariableKeyword, IsKeyword, EndToken, BeginKeyword, FunctionKeyword, ReportKeyword
from pyVHDLParser.Blocks                    import Block, TokenParserException, CommentBlock, ParserState
from pyVHDLParser.Blocks.Common             import LinebreakBlock, IndentationBlock, WhitespaceBlock
# from pyVHDLParser.Blocks.ControlStructure   import If, Case, ForLoop, WhileLoop, Return
from pyVHDLParser.Blocks.Generic            import EndBlock as EndBlockBase, SequentialBeginBlock
from pyVHDLParser.Blocks.List               import GenericList, ParameterList
from pyVHDLParser.Blocks.Object             import ConstantDeclarationBlock, ConstantDeclarationEndMarkerBlock, VariableDeclarationBlock, VariableDeclarationEndMarkerBlock
from pyVHDLParser.Blocks.Reference          import Use
from pyVHDLParser.Blocks.Reporting.Report   import ReportBlock
from pyVHDLParser.Blocks.Sequential         import Function


class NameBlock(Block):
	@classmethod
	def stateProcedureKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken = BoundaryToken(token)
			parserState.NextState = cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected whitespace after keyword PROCEDURE.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			parserState.NewToken = IdentifierToken(token)
			parserState.NextState = cls.stateProcedureName
			return
		elif isinstance(token, LinebreakToken):
			if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
				parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				_ = LinebreakBlock(parserState.NewBlock, token)
			else:
				parserState.NewBlock = LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock = CommentBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken = BoundaryToken(token)
			parserState.NewBlock = WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker = None
			return

		raise TokenParserException("Expected procedure name (designator).", token)

	@classmethod
	def stateProcedureName(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken) and (token == "(")):
			parserState.NewToken = BoundaryToken(token)
			parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
			_ = ParameterList.OpenBlock(parserState.NewBlock, parserState.NewToken)
			parserState.TokenMarker = None
			parserState.NextState = VoidBlock.stateAfterParameterList
			parserState.PushState = ParameterList.OpenBlock.stateOpeningParenthesis
			parserState.Counter = 1
			return
		elif isinstance(token, SpaceToken):
			parserState.NewToken = BoundaryToken(token)
			parserState.NextState = cls.stateWhitespace2
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace2
			return

		raise TokenParserException("Expected '(' or whitespace after procedure name.", token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken) and (token == "(")):
			parserState.NewToken = BoundaryToken(token)
			parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
			_ = ParameterList.OpenBlock(parserState.NewBlock, parserState.NewToken)
			parserState.TokenMarker = None
			parserState.NextState = VoidBlock.stateAfterParameterList
			parserState.PushState = ParameterList.OpenBlock.stateOpeningParenthesis
			parserState.Counter = 1
			return
		elif isinstance(token, StringToken):
			keyword = token.Value.lower()
			if (keyword == "is"):
				parserState.NewToken =    IsKeyword(token)
				parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
				_ =                       VoidBlock(parserState.NewBlock, parserState.NewToken)
				parserState.TokenMarker = parserState.NewToken
				parserState.NextState =   VoidBlock.stateDeclarativeRegion
				return
			elif (keyword == "generic"):
				parserState.NewToken = GenericKeyword(token)
				parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.NextState = GenericList.OpenBlock.stateGenericKeyword
				return
			elif (keyword == "parameter"):
				parserState.NewToken = ParameterKeyword(token)
				parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
				parserState.NextState = ParameterList.OpenBlock.stateParameterKeyword
				return
		elif isinstance(token, LinebreakToken):
			if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
				parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				_ = LinebreakBlock(parserState.NewBlock, token)
			else:
				parserState.NewBlock = LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock = cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ = CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken = BoundaryToken(token)
			parserState.NewBlock = WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker = None
			return

		raise TokenParserException("Expected '(' or keywords GENERIC, PARAMETER or RETURN after procedure name.", token)


class VoidBlock(Block):
	@classmethod
	def stateAfterParameterList(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken) and (token == ";")):
			parserState.NewToken =    EndToken(token)
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.Pop()
			return
		elif isinstance(token, StringToken):
			if (token <= "is"):
				parserState.NewToken =  IsKeyword(token)
				parserState.NewBlock =  VoidBlock(parserState.LastBlock, parserState.TokenMarker, parserState.NewToken)
				parserState.NextState = cls.stateDeclarativeRegion
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    block(parserState.LastBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected keyword RETURN.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, StringToken) and (token <= "is")):
			parserState.NewToken =    IsKeyword(token)
			parserState.NextState =   cls.stateDeclarativeRegion
			return
		elif isinstance(token, LinebreakToken):
			if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
				parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
				_ =                     LinebreakBlock(parserState.NewBlock, token)
			else:
				parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    CommentBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NewBlock =    WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker = None
			return

		raise TokenParserException("Expected procedure name (designator).", token)

	@classmethod
	def stateDeclarativeRegion(cls, parserState: ParserState):
		keywords = {
			# Keyword     Transition
			UseKeyword:       Use.StartBlock.stateUseKeyword,
			ConstantKeyword:  ConstantDeclarationBlock.stateConstantKeyword,
			VariableKeyword:  VariableDeclarationBlock.stateVariableKeyword,
			FunctionKeyword:  Function.NameBlock.stateFunctionKeyword,
			ProcedureKeyword: NameBlock.stateProcedureKeyword,
			ReportKeyword:    ReportBlock.stateReportKeyword,
			ImpureKeyword:    Function.NameBlock.stateImpureKeyword,
			PureKeyword:      Function.NameBlock.statePureKeyword
		}

		token = parserState.Token
		if isinstance(token, SpaceToken):
			blockType =               IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =    blockType(parserState.LastBlock, token)
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    block(parserState.LastBlock, token)
			parserState.TokenMarker = None
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
				parserState.NewToken =    BeginKeyword(token)
				parserState.NewBlock =    BeginBlock(parserState.LastBlock, parserState.NewToken)
				parserState.TokenMarker = None
				parserState.NextState =   BeginBlock.stateSequentialRegion
				return
			elif (tokenValue == "end"):
				parserState.NewToken =    EndKeyword(token)
				parserState.NextState =   EndBlock.stateEndKeyword
				parserState.TokenMarker = parserState.NewToken
				return

		raise TokenParserException(
			"Expected one of these keywords: END, {keywords}. Found: '{tokenValue}'.".format(
				keywords=", ".join(
					[kw.__KEYWORD__.upper() for kw in keywords]
				),
				tokenValue=token.Value
			), token)


class EndBlock(EndBlockBase):
	KEYWORD = ProcedureKeyword
	KEYWORD_IS_OPTIONAL = True
	EXPECTED_NAME = KEYWORD.__KEYWORD__


class BeginBlock(SequentialBeginBlock):
	END_BLOCK = EndBlock
