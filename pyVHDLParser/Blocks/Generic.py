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
from pyVHDLParser.Blocks import TokenParserException, Block, CommentBlock, ParserState
from pyVHDLParser.Blocks.Common import LinebreakBlock, WhitespaceBlock, IndentationBlock
from pyVHDLParser.Blocks.ControlStructure.If import IfConditionBlock
from pyVHDLParser.Blocks.Generic1 import EndBlock
from pyVHDLParser.Blocks.Reporting.Assert import AssertBlock
from pyVHDLParser.Blocks.Reporting.Report import ReportBlock
from pyVHDLParser.Token import LinebreakToken, CommentToken, IndentationToken
from pyVHDLParser.Token.Keywords import AssertKeyword, EndKeyword, ProcessKeyword, ReportKeyword, \
	IfKeyword
from pyVHDLParser.Token.Parser import SpaceToken, StringToken


class ConcurrentBeginBlock(Block):
	END_BLOCK : EndBlock = None

	@classmethod
	def stateConcurrentRegion(cls, parserState: ParserState):
		from pyVHDLParser.Blocks.Sequential import Process

		keywords = {
			# Keyword     Transition
			AssertKeyword:      AssertBlock.stateAssertKeyword,
			ProcessKeyword:     Process.OpenBlock.stateProcessKeyword,
		}

		token = parserState.Token
		if isinstance(token, SpaceToken):
			blockType =               IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =    blockType(parserState.LastBlock, token)
			parserState.TokenMarker = None
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
					newToken = keyword(token)
					parserState.PushState = keywords[keyword]
					parserState.NewToken = newToken
					parserState.TokenMarker = newToken
					return

			if (tokenValue == "end"):
				parserState.NewToken =  EndKeyword(token)
				parserState.NextState = cls.END_BLOCK.stateEndKeyword
				return

		raise TokenParserException(
			"Expected one of these keywords: END, {keywords}. Found: '{tokenValue}'.".format(
				keywords=", ".join(
					[kw.__KEYWORD__.upper() for kw in keywords]
				),
				tokenValue=token.Value
			), token)


class SequentialBeginBlock(Block):
	END_BLOCK : EndBlock = None

	@classmethod
	def stateSequentialRegion(cls, parserState: ParserState):
		keywords = {
			# Keyword     Transition
			IfKeyword:          IfConditionBlock.stateIfKeyword,
			ReportKeyword:      ReportBlock.stateReportKeyword,
			# ProcessKeyword:     Process.NameBlock.stateProcesdureKeyword,
		}

		token = parserState.Token
		if isinstance(token, SpaceToken):
			blockType =               IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =    blockType(parserState.LastBlock, token)
			parserState.TokenMarker = None
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
					newToken = keyword(token)
					parserState.PushState = keywords[keyword]
					parserState.NewToken = newToken
					parserState.TokenMarker = newToken
					return

			if (tokenValue == "end"):
				parserState.NewToken =  EndKeyword(token)
				parserState.NextState = cls.END_BLOCK.stateEndKeyword
				return

		raise TokenParserException(
			"Expected one of these keywords: END, {keywords}. Found: '{tokenValue}'.".format(
				keywords=", ".join(
					[kw.__KEYWORD__.upper() for kw in keywords]
				),
				tokenValue=token.Value
			), token)


