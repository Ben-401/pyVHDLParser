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
from pyVHDLParser.Token           import LinebreakToken, CommentToken, MultiLineCommentToken, IndentationToken, SingleLineCommentToken, ExtendedIdentifier
from pyVHDLParser.Token.Parser    import StringToken, SpaceToken
from pyVHDLParser.Token.Keywords  import EntityKeyword, IsKeyword, GenericKeyword, PortKeyword
from pyVHDLParser.Token.Keywords  import BoundaryToken, IdentifierToken
from pyVHDLParser.Blocks          import TokenParserException, Block, CommentBlock, ParserState
from pyVHDLParser.Blocks.Common   import LinebreakBlock, WhitespaceBlock
from pyVHDLParser.Blocks.Generic  import ConcurrentBeginBlock, ConcurrentDeclarativeRegion
from pyVHDLParser.Blocks.Generic1 import EndBlock as EndBlockBase


class EndBlock(EndBlockBase):
	KEYWORD =             EntityKeyword
	KEYWORD_IS_OPTIONAL = True
	EXPECTED_NAME =       KEYWORD.__KEYWORD__


class BeginBlock(ConcurrentBeginBlock):
	END_BLOCK =   EndBlock


class DeclarativeRegion(ConcurrentDeclarativeRegion):
	BEGIN_BLOCK = BeginBlock
	END_BLOCK =   EndBlock

	@classmethod
	def __cls_init__(cls):
		super().__cls_init__()

		from pyVHDLParser.Blocks.List.GenericList import OpenBlock as GenericListOpenBlock
		from pyVHDLParser.Blocks.List.PortList    import OpenBlock as PortListOpenBlock

		cls.KEYWORDS.update({
			# Keyword         Transition
			GenericKeyword:   GenericListOpenBlock.stateGenericKeyword,
			PortKeyword:      PortListOpenBlock.statePortKeyword
		})


class NameBlock(Block):
	@classmethod
	def stateEntityKeyword(cls, parserState: ParserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken =    BoundaryToken(token)
			parserState.NextState =   cls.stateWhitespace1
			return
		elif isinstance(token, (LinebreakToken, CommentToken)):
			block =                   LinebreakBlock if isinstance(token, LinebreakToken) else CommentBlock
			parserState.NewBlock =    cls(parserState.LastBlock, parserState.TokenMarker, endToken=token.PreviousToken, multiPart=True)
			_ =                       block(parserState.NewBlock, token)
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
		elif isinstance(token, ExtendedIdentifier):
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

		raise TokenParserException("Expected entity name (identifier).", token)

	@classmethod
	def stateEntityName(cls, parserState: ParserState):
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
		if (isinstance(token, StringToken) and (token <= "is")):
			parserState.NewToken =      IsKeyword(token)
			parserState.NewBlock =      cls(parserState.LastBlock, parserState.TokenMarker, endToken=parserState.NewToken)
			parserState.TokenMarker =   None
			parserState.NextState =     DeclarativeRegion.stateDeclarativeRegion
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
