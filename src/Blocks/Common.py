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
from src.Blocks.Exception import BlockParserException
from src.Token.Keywords       import *
from src.Token.Parser         import CharacterToken, SpaceToken
from src.Blocks.Base          import Block
# from src.Blocks.Comment       import SingleLineCommentBlock, MultiLineCommentBlock


class WhitespaceBlock(Block):
	def __init__(self, previousBlock, startToken):
		super().__init__(previousBlock, startToken, startToken)

	def __str__(self):
		return "[{blockName: <30s}  {stream}  at {start!s} .. {end!s}]".format(
			blockName=type(self).__name__,
			stream=" "*60,
			start=self.StartToken.Start,
			end=self.EndToken.End
		)


class LinebreakBlock(WhitespaceBlock):
	@classmethod
	def stateLinebreak(cls, parserState):
		token = parserState.Token
		if isinstance(token, SpaceToken):
			parserState.NewToken = IndentationToken(token)
			parserState.NewBlock = IndentationBlock(parserState.LastBlock, parserState.NewToken)
			parserState.Pop()
		else:
			parserState.Pop()
			if (parserState.TokenMarker is None):
				# print("  new marker: None -> {0!s}".format(token))
				parserState.TokenMarker = token
			# print("  re-issue: {0!s}".format(parserState))
			parserState.NextState(parserState)


class EmptyLineBlock(LinebreakBlock):
	pass


class IndentationBlock(WhitespaceBlock):
	__TABSIZE__ = 2

	def __str__(self):
		length = len(self.StartToken.Value)
		actual = sum([(self.__TABSIZE__ if (c == "\t") else 1) for c in self.StartToken.Value])

		return "[{blockName: <30s}  length={len: <53}  at {start!s} .. {end!s}]".format(
			blockName=type(self).__name__,
			len="{len} ({actual}) ".format(len=length, actual=actual),
			start=self.StartToken.Start,
			end=self.EndToken.End
		)
