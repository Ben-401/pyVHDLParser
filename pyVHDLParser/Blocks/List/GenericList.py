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
from pyVHDLParser.Blocks.Expression.Expression import ExpressionBlock
from pyVHDLParser.Token import CharacterToken, LinebreakToken, IndentationToken, CommentToken, MultiLineCommentToken, SingleLineCommentToken, \
	ExtendedIdentifier, FusedCharacterToken
from pyVHDLParser.Token.Keywords import BoundaryToken, EndToken, DelimiterToken, ClosingRoundBracketToken, ConstantKeyword, InKeyword, VariableAssignmentKeyword
from pyVHDLParser.Token.Keywords       import IdentifierToken
from pyVHDLParser.Token.Parser         import SpaceToken, StringToken
from pyVHDLParser.Blocks               import TokenParserException, Block, CommentBlock, ParserState, SkipableBlock
from pyVHDLParser.Blocks.Common        import LinebreakBlock, IndentationBlock, WhitespaceBlock


class OpenBlock(Block):
	@classmethod
	def stateGenericKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken)and (token == "(")):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.NextState =   CloseBlock.stateClosingParenthesis
			parserState.PushState =   cls.stateOpeningParenthesis
			parserState.Counter =     1
			return
		elif isinstance(token, SpaceToken):
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected '(' or whitespace after keyword GENERIC.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken)and (token == "(")):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.NextState =   CloseBlock.stateClosingParenthesis
			parserState.PushState =   cls.stateOpeningParenthesis
			parserState.Counter =     1
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
		elif (isinstance(token, IndentationToken) and isinstance(token.PreviousToken, (LinebreakToken, SingleLineCommentToken))):
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NewBlock =    WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker = None
			return

		raise TokenParserException("Expected '(' after keyword GENERIC.", token)

	@classmethod
	def stateOpeningParenthesis(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken)and (token == ")")):
			# if (parserState.TokenMarker != token):
			# 	parserState.NewBlock = IndentationBlock(parserState.LastBlock, parserState.TokenMarker, token.PreviousToken)
			parserState.Pop()
			parserState.TokenMarker = token
			return
		elif isinstance(token, StringToken):
			if (token <= "constant"):
				parserState.NewToken =    ConstantKeyword(token)
				parserState.TokenMarker = parserState.NewToken
				parserState.NextState =   InterfaceConstantBlock.stateConstantKeyword
				return
			elif (token <= "type"):
				raise NotImplementedError("Generic types are not supported.")
			elif (token <= "procedure"):
				raise NotImplementedError("Generic procedures are not supported.")
			elif (token <= "function"):
				raise NotImplementedError("Generic functions are not supported.")
			elif (token <= "impure"):
				raise NotImplementedError("Generic impure functions are not supported.")
			elif (token <= "pure"):
				raise NotImplementedError("Generic pure functions are not supported.")
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.TokenMarker = parserState.NewToken
				parserState.NextState =   InterfaceConstantBlock.stateConstantName
				return
		elif isinstance(token, ExtendedIdentifier):
			parserState.NextState =   InterfaceConstantBlock.stateConstantName
			return
		elif isinstance(token, SpaceToken):
			blockType =               IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =    blockType(parserState.LastBlock, token)
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = token
			# parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			# parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected interface element name (identifier).", token)


class InterfaceConstantBlock(Block):
	@classmethod
	def stateConstantKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected whitespace after keyword CONSTANT.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			parserState.NewToken =      IdentifierToken(token)
			parserState.NextState =     cls.stateConstantName
			return
		elif isinstance(token, ExtendedIdentifier):
			parserState.NextState =     cls.stateConstantName
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

		raise TokenParserException("Expected interface constant name (identifier).", token)



		# token = parserState.Token
		# if (isinstance(token, CharacterToken)and (token == "(")):
		# 	parserState.NewToken =    BoundaryToken(token)
		# 	parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
		# 	parserState.NextState =   CloseBlock.stateClosingParenthesis
		# 	parserState.PushState =   cls.stateOpeningParenthesis
		# 	parserState.Counter =     1
		# 	return
		# elif isinstance(token, LinebreakToken):
		# 	if (not (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
		# 		parserState.NewBlock =  cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
		# 		_ =                     LinebreakBlock(parserState.NewBlock, token)
		# 	else:
		# 		parserState.NewBlock =  LinebreakBlock(parserState.LastBlock, token)
		# 	parserState.TokenMarker = None
		# 	return
		# elif isinstance(token, CommentToken):
		# 	parserState.NewBlock =    CommentBlock(parserState.LastBlock, token)
		# 	parserState.TokenMarker = None
		# 	return
		# elif (isinstance(token, IndentationToken) and isinstance(token.PreviousToken, (LinebreakToken, SingleLineCommentToken))):
		# 	return
		# elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
		# 	parserState.NewToken =    BoundaryToken(token)
		# 	parserState.NewBlock =    WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
		# 	parserState.TokenMarker = None
		# 	return
		#
		# raise TokenParserException("Expected '(' after keyword GENERIC.", token)

	@classmethod
	def stateConstantName(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace2
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace2
			return

		raise TokenParserException("Expected whitespace after entity name.", token)

	@classmethod
	def stateWhitespace2(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken) and (token == ":")):
			parserState.NewToken =      DelimiterToken(token)
			parserState.NextState =     cls.stateColon1
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

		raise TokenParserException("Expected ':' after interface constant name.", token)

	@classmethod
	def stateColon1(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			if (token <= "in"):
				parserState.NewToken =  InKeyword(token)
				parserState.NextState = cls.stateInKeyword
				return
			else:
				parserState.NewToken =  IdentifierToken(token)
				parserState.NextState = cls.stateSubtypeIndication
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace3
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace3
			return

		raise TokenParserException("Expected type (type mark) or whitespace after colon.", token)

	@classmethod
	def stateWhitespace3(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			if (token <= "in"):
				parserState.NewToken =    InKeyword(token)
				parserState.NextState =   cls.stateInKeyword
				return
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.NextState =   cls.stateSubtypeIndication
				return
		elif isinstance(token, ExtendedIdentifier):
			parserState.NextState =     cls.stateSubtypeIndication
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

		raise TokenParserException("Expected subtype indication (name) or keyword IN.", token)

	@classmethod
	def stateInKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NextState =   cls.stateWhitespace4
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace4
			return

		raise TokenParserException("Expected whitespace after keyword CONSTANT.", token)

	@classmethod
	def stateWhitespace4(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			parserState.NewToken =      IdentifierToken(token)
			parserState.NextState =     cls.stateSubtypeIndication
			return
		elif isinstance(token, ExtendedIdentifier):
			parserState.NextState =     cls.stateSubtypeIndication
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

		raise TokenParserException("Expected subtype indication (name).", token)

	@classmethod
	def stateSubtypeIndication(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, FusedCharacterToken) and (token == ":=")):
			parserState.NewToken =      VariableAssignmentKeyword(token)
			parserState.NewBlock =      InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.NextState =     DelimiterBlock.stateItemDelimiter
			parserState.PushState =     ExpressionBlock.stateExpression
			parserState.TokenMarker =   None
			parserState.Counter =       0
			return
		elif isinstance(token, CharacterToken):
			if (token == ';'):
				parserState.NewToken =    DelimiterToken(token)
				parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
				_ =                       DelimiterBlock(parserState.NewBlock, parserState.NewToken)
				parserState.NextState =   DelimiterBlock.stateItemDelimiter
				return
			elif (token == ')'):
				parserState.NewToken =    BoundaryToken(token)
				parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
				parserState.Pop()
				parserState.TokenMarker = parserState.NewToken
				return
		elif isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace5
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace5
			return

		raise TokenParserException("Expected ';', ':=' or whitespace after subtype indication.", token)

	@classmethod
	def stateWhitespace5(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, FusedCharacterToken) and (token == ":=")):
			parserState.NewToken =      VariableAssignmentKeyword(token)
			parserState.NewBlock =      InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.NextState =     DelimiterBlock.stateItemDelimiter
			parserState.PushState =     ExpressionBlock.stateExpression
			parserState.TokenMarker =   None
			parserState.Counter =       0
			return
		elif isinstance(token, CharacterToken):
			if (token == ';'):
				parserState.NewToken =    DelimiterToken(token)
				parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
				_ =                       DelimiterBlock(parserState.NewBlock, parserState.NewToken)
				parserState.NextState =   DelimiterBlock.stateItemDelimiter
				return
			elif (token == ')'):
				parserState.NewToken =    BoundaryToken(token)
				parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
				parserState.Pop()
				parserState.TokenMarker = parserState.NewToken
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

		raise TokenParserException("Expected ';' or ':='.", token)


		# token = parserState.Token
		# if isinstance(token, CharacterToken):
		# 	if (token == "("):
		# 		parserState.Counter += 1
		# 	elif (token == ")"):
		# 		parserState.Counter -= 1
		# 		if (parserState.Counter == 0):
		# 			parserState.NewToken =    BoundaryToken(token)
		# 			parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
		# 			parserState.Pop()
		# 			parserState.TokenMarker = parserState.NewToken
		# 		else:
		# 			parserState.NewToken =    ClosingRoundBracketToken(token)
		# 	elif (token == ";"):
		# 		if (parserState.Counter == 1):
		# 			parserState.NewToken =    DelimiterToken(token)
		# 			parserState.NewBlock =    InterfaceConstantBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken.PreviousToken)
		# 			_ =                       DelimiterBlock(parserState.NewBlock, parserState.NewToken)
		# 			parserState.NextState =   DelimiterBlock.stateItemDelimiter
		# 		else:
		# 			raise TokenParserException("Mismatch in opening and closing parenthesis: open={0}".format(parserState.Counter), token)


class DelimiterBlock(SkipableBlock):
	def __init__(self, previousBlock, startToken):
		super().__init__(previousBlock, startToken, startToken)

	@classmethod
	def stateItemDelimiter(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, StringToken):
			if (token <= "constant"):
				parserState.NewToken =    ConstantKeyword(token)
				parserState.TokenMarker = parserState.NewToken
				parserState.NextState =   InterfaceConstantBlock.stateConstantKeyword
				return
			elif (token <= "type"):
				raise NotImplementedError("Generic types are not supported.")
			elif (token <= "procedure"):
				raise NotImplementedError("Generic procedures are not supported.")
			elif (token <= "function"):
				raise NotImplementedError("Generic functions are not supported.")
			elif (token <= "impure"):
				raise NotImplementedError("Generic impure functions are not supported.")
			elif (token <= "pure"):
				raise NotImplementedError("Generic pure functions are not supported.")
			else:
				parserState.NewToken =    IdentifierToken(token)
				parserState.TokenMarker = parserState.NewToken
				parserState.NextState =   InterfaceConstantBlock.stateConstantName
				return
		elif isinstance(token, ExtendedIdentifier):
			parserState.NextState =   InterfaceConstantBlock.stateConstantName
			return
		elif isinstance(token, SpaceToken):
			parserState.NextState =   OpenBlock.stateOpeningParenthesis
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = token
			parserState.NextState =   OpenBlock.stateOpeningParenthesis
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       CommentBlock(parserState.NewBlock, token)
			parserState.TokenMarker = None
			# parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected generic name (identifier).", token)


class CloseBlock(Block):
	@classmethod
	def stateClosingParenthesis(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken) and (token == ";")):
			parserState.NewToken =    EndToken(token)
			parserState.NewBlock =    CloseBlock(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.Pop()
			return
		elif isinstance(token, SpaceToken):
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
			parserState.TokenMarker = None
			parserState.NextState =   cls.stateWhitespace1
			return

		raise TokenParserException("Expected ';' or whitespace.", token)

	@classmethod
	def stateWhitespace1(cls, parserState: ParserState):
		token = parserState.Token
		if (isinstance(token, CharacterToken)and (token == ";")):
			parserState.NewToken =    EndToken(token)
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.Pop()
			return
		elif isinstance(token, LinebreakToken):
			# TODO: review this linebreak case
			parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    CommentBlock(parserState.LastBlock, token)
			parserState.TokenMarker = token
			return
		elif (isinstance(token, IndentationToken) and isinstance(token.PreviousToken, (LinebreakToken, SingleLineCommentToken))):
			return
		elif (isinstance(token, SpaceToken) and (isinstance(parserState.LastBlock, CommentBlock) and isinstance(parserState.LastBlock.StartToken, MultiLineCommentToken))):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NewBlock =    WhitespaceBlock(parserState.LastBlock, parserState.NewToken)
			parserState.TokenMarker = None
			return

		raise TokenParserException("Expected ';'.", token)
