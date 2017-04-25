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
from pyVHDLParser.Token import CharacterToken, LinebreakToken, IndentationToken, CommentToken, MultiLineCommentToken, SingleLineCommentToken, \
	ExtendedIdentifier, FusedCharacterToken, LiteralToken
from pyVHDLParser.Token.Keywords import BoundaryToken, EndToken, DelimiterToken, ClosingRoundBracketToken, ConstantKeyword, InKeyword, \
	VariableAssignmentKeyword, LessThanOrEqualOperator, UnequalOperator, GreaterThanOrEqualOperator, MatchingEqualOperator, MatchingUnequalOperator, \
	MatchingLessThanOperator, MatchingLessThanOrEqualOperator, MatchingGreaterThanOperator, MatchingGreaterThanOrEqualOperator, OrKeyword, NorKeyword, AndKeyword, \
	NandKeyword, XorKeyword, XnorKeyword, SlaKeyword, SllKeyword, SraKeyword, SrlKeyword, NotKeyword, AbsKeyword, PowerOperator, PlusOperator, MinusOperator, \
	MultiplyOperator, DivideOperator, ConcatOperator, OpeningRoundBracketToken
from pyVHDLParser.Token.Keywords       import IdentifierToken
from pyVHDLParser.Token.Parser         import SpaceToken, StringToken
from pyVHDLParser.Blocks               import TokenParserException, Block, CommentBlock, ParserState, SkipableBlock
from pyVHDLParser.Blocks.Common        import LinebreakBlock, IndentationBlock, WhitespaceBlock


class ExpressionBlock(Block):
	CHARACTER_TRANSLATION = {
		"+":    PlusOperator,
		"-":    MinusOperator,
		"*":    MultiplyOperator,
		"/":    DivideOperator,
		"&":    ConcatOperator
	}
	FUSED_CHARACTER_TRANSLATION = {
		"**":   PowerOperator,
		"/=":   UnequalOperator,
		"<=":   LessThanOrEqualOperator,
		">=":   GreaterThanOrEqualOperator,
		"?=":   MatchingEqualOperator,
		"?/=":  MatchingUnequalOperator,
		"?<":   MatchingLessThanOperator,
		"?<=":  MatchingLessThanOrEqualOperator,
		"?>":   MatchingGreaterThanOperator,
		"?>=":  MatchingGreaterThanOrEqualOperator
	}
	OPERATOR_TRANSLATIONS = {
		"or":    OrKeyword,
		"nor":   NorKeyword,
		"and":   AndKeyword,
		"nand":  NandKeyword,
		"xor":   XorKeyword,
		"xnor":  XnorKeyword,
		"sla":   SlaKeyword,
		"sll":   SllKeyword,
		"sra":   SraKeyword,
		"srl":   SrlKeyword,
		"not":   NotKeyword,
		"abs":   AbsKeyword

	}

	@classmethod
	def stateExpression(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, FusedCharacterToken):
			parserState.NewToken = cls.FUSED_CHARACTER_TRANSLATION[token.Value](token)
			return
		elif isinstance(token, CharacterToken):
			if (token == ";"):
				if (parserState.Counter == 0):
					parserState.NewToken =  DelimiterToken(token)
					parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
					parserState.Pop()
					return
				else:
					raise TokenParserException("Mismatch in opening and closing parenthesis. Counter={0}".format(parserState.Counter), token)
			elif (token == "("):
				parserState.NewToken =    OpeningRoundBracketToken(token)
				parserState.Counter +=    1
				return
			elif (token == ")"):
				if (parserState.Counter == 0):
					parserState.NewToken =  BoundaryToken(token)
					parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
					parserState.Pop(2)
					return
				else:
					parserState.NewToken =  ClosingRoundBracketToken(token)
					parserState.Counter -=  1
					return
			else:
				parserState.NewToken =    cls.CHARACTER_TRANSLATION[token.Value](token)
				return
		elif isinstance(token, StringToken):
			try:
				parserState.NewToken =    cls.OPERATOR_TRANSLATIONS[token.Value](token)
			except KeyError:
				parserState.NewToken =    IdentifierToken(token)
			return
		elif isinstance(token, LiteralToken):
			return
		elif isinstance(token, SpaceToken):
			parserState.NextState =     cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                     LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =      cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                         block(parserState.NewBlock, token)
			parserState.TokenMarker =   None
			parserState.NextState =     cls.stateWhitespace1
			return

		raise TokenParserException("Expected '(' or whitespace after keyword GENERIC.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, FusedCharacterToken):
			parserState.NewToken =    cls.FUSED_CHARACTER_TRANSLATION[token.Value](token)
			parserState.NextState =   cls.stateExpression
			return
		elif isinstance(token, CharacterToken):
			if (token == ";"):
				if (parserState.Counter == 0):
					parserState.NewToken =  DelimiterToken(token)
					parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
					parserState.Pop()
					return
				else:
					raise TokenParserException("Mismatch in opening and closing parenthesis. Counter={0}".format(parserState.Counter), token)
			elif (token == "("):
				parserState.NewToken =    OpeningRoundBracketToken(token)
				parserState.Counter +=    1
				parserState.NextState =   cls.stateExpression
				return
			elif (token == ")"):
				if (parserState.Counter == 0):
					parserState.NewToken =  BoundaryToken(token)
					parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
					parserState.Pop(2)
					return
				else:
					parserState.NewToken =  ClosingRoundBracketToken(token)
					parserState.Counter -=  1
					parserState.NextState = cls.stateExpression
					return
			else:
				parserState.NewToken =    cls.CHARACTER_TRANSLATION[token.Value](token)
				parserState.NextState =   cls.stateExpression
				return
		elif isinstance(token, StringToken):
			try:
				parserState.NewToken =    cls.OPERATOR_TRANSLATIONS[token.Value](token)
			except KeyError:
				parserState.NewToken =    IdentifierToken(token)
			parserState.NextState =     cls.stateExpression
			return
		elif isinstance(token, LiteralToken):
			parserState.NextState =     cls.stateExpression
			parserState.NextState =     cls.stateExpression
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

		raise TokenParserException("Expected ????????????.", token)
