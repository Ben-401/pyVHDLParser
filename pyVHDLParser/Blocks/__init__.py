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
from types                          import FunctionType

from pyVHDLParser                   import StartOfDocument, EndOfDocument, StartOfSnippet, EndOfSnippet
from pyVHDLParser.Base              import ParserException
from pyVHDLParser.Token             import CharacterToken, Token, SpaceToken, IndentationToken, LinebreakToken, CommentToken, StringToken, EndOfDocumentToken
from pyVHDLParser.Token.Keywords    import LibraryKeyword, UseKeyword, ContextKeyword, EntityKeyword, ArchitectureKeyword, PackageKeyword
from pyVHDLParser.Functions         import Console


class TokenParserException(ParserException):
	def __init__(self, message, token):
		super().__init__(message)
		self._token = token


class TokenToBlockParser:
	@staticmethod
	def Transform(tokenGenerator, debug=False):
		return ParserState(tokenGenerator, debug=debug).GetGenerator()


class ParserState:
	def __init__(self, tokenGenerator, debug):
		self._stack =               []
		self._iterator =            iter(tokenGenerator)
		self._tokenMarker : Token = None
		self.NextState =            StartOfDocumentBlock.stateDocument
		self.LastBlock    : Block = None
		self.NewBlock     : Block = StartOfDocumentBlock(next(self._iterator))
		self.Token        : Token = self.NewBlock.StartToken
		self.NewToken     : Token = None
		self.Counter =              0

		self.debug        : bool =  debug

	@property
	def PushState(self):
		return self.NextState
	@PushState.setter
	def PushState(self, value):
		self._stack.append((
			self.NextState,
			self.Counter
		))
		self.NextState =    value
		self._tokenMarker =  None

	@property
	def TokenMarker(self):
		if ((self.NewToken is not None) and (self._tokenMarker is self.Token)):
			if self.debug: print("  {DARK_GREEN}@TokenMarker: {0!s} => {GREEN}{1!s}{NOCOLOR}".format(self._tokenMarker, self.NewToken, **Console.Foreground))
			self._tokenMarker = self.NewToken
		return self._tokenMarker
	@TokenMarker.setter
	def TokenMarker(self, value):
		self._tokenMarker = value

	def __eq__(self, other):
		return self.NextState is other

	def __str__(self):
		return self.NextState.__func__.__qualname__

	def Pop(self, n=1):
		top = None
		for i in range(n):
			top = self._stack.pop()
		self.NextState =    top[0]
		self.Counter =      top[1]
		self._tokenMarker = None

	def GetGenerator(self):
		from pyVHDLParser.Token             import EndOfDocumentToken
		from pyVHDLParser.Blocks            import TokenParserException, EndOfDocumentBlock
		from pyVHDLParser.Blocks.Common     import LinebreakBlock, EmptyLineBlock

		for token in self._iterator:
			# overwrite an existing token and connect the next token with the new one
			if (self.NewToken is not None):
				# print("{MAGENTA}NewToken: {token}{NOCOLOR}".format(token=self.NewToken, **Console.Foreground))
				# update topmost TokenMarker
				if (self._tokenMarker is token.PreviousToken):
					if self.debug: print("  update token marker: {0!s} -> {1!s}".format(self._tokenMarker, self.NewToken))
					self._tokenMarker = self.NewToken

				token.PreviousToken = self.NewToken
				self.NewToken =       None

			self.Token = token
			# an empty marker means: fill on next yield run
			if (self._tokenMarker is None):
				if self.debug: print("  new token marker: None -> {0!s}".format(token))
				self._tokenMarker = token

			# a new block is assembled
			while (self.NewBlock is not None):
				if (isinstance(self.NewBlock, LinebreakBlock) and isinstance(self.LastBlock, (LinebreakBlock, EmptyLineBlock))):
					self.LastBlock = EmptyLineBlock(self.LastBlock, self.NewBlock.StartToken)
					self.LastBlock.NextBlock = self.NewBlock.NextBlock
				else:
					self.LastBlock = self.NewBlock

				self.NewBlock =  self.NewBlock.NextBlock
				yield self.LastBlock

			# if self.debug: print("{MAGENTA}------ iteration end ------{NOCOLOR}".format(**Console.Foreground))
			if self.debug: print("  {DARK_GRAY}state={state!s: <50}  token={token!s: <40}{NOCOLOR}   ".format(state=self, token=token, **Console.Foreground))
			# execute a state
			self.NextState(self)

		else:
			if (isinstance(self.Token, EndOfDocumentToken) and isinstance(self.NewBlock, EndOfDocumentBlock)):
				yield self.NewBlock
			else:
				raise TokenParserException("Unexpected end of document.", self.Token)


class MetaBlock(type):
	"""Register all state*** methods in an array called '__STATES__'"""
	def __new__(cls, className, baseClasses, classMembers : dict):
		states = []
		for memberName, memberObject in classMembers.items():
			if (isinstance(memberObject, FunctionType) and (memberName[:5] == "state")):
				states.append(memberObject)

		classMembers['__STATES__'] = states
		return super().__new__(cls, className, baseClasses, classMembers)


class Block(metaclass=MetaBlock):
	__STATES__ = None

	def __init__(self, previousBlock, startToken, endToken=None, multiPart=False):
		previousBlock.NextBlock =     self
		self._previousBlock : Block = previousBlock
		self.NextBlock      : Block = None
		self.StartToken     : Token = startToken
		self.EndToken       : Token = startToken if (endToken is None) else endToken
		self.MultiPart =              multiPart

	def __len__(self):
		return self.EndToken.End.Absolute - self.StartToken.Start.Absolute + 1

	def __iter__(self):
		token = self.StartToken
		# print("block={0}({1})  start={2!s}  end={3!s}".format(self.__class__.__name__, self.__class__.__module__, self.StartToken, self.EndToken))
		while (token is not self.EndToken):
			yield token
			if (token.NextToken is None):
				raise TokenParserException("Token after {0!r} ==> {1!r} ==> {2!r} is None.".format(token.PreviousToken.PreviousToken, token.PreviousToken, token), token)
			token = token.NextToken

		yield self.EndToken

	def __repr__(self):
		buffer = ""
		for token in self:
			if isinstance(token, CharacterToken):
				buffer += repr(token)
			else:
				buffer += token.Value

		buffer = buffer.replace("\t", "\\t")
		buffer = buffer.replace("\n", "\\n")
		return buffer

	def __str__(self):
		return "[{blockName: <30s} {stream: <62s} at {start!s} .. {end!s}]".format(
			blockName="{module}.{classname}{multiparted}".format(
				module=self.__module__.rpartition(".")[2],
				classname=self.__class__.__name__,
				multiparted=("*" if self.MultiPart else "")
			),
			stream="'" + repr(self) + "'",
			start=self.StartToken.Start,
			end=self.EndToken.End
		)

	@property
	def PreviousBlock(self):
		return self._previousBlock
	@PreviousBlock.setter
	def PreviousBlock(self, value):
		self._previousBlock = value
		value.NextBlock = self

	@property
	def Length(self):
		return len(self)

	@property
	def States(self):
		return self.__STATES__


class CommentBlock(Block):
	pass


class StartOfBlock(Block):
	def __init__(self, startToken):
		self._previousBlock =     None
		self.NextBlock =          None
		self.StartToken =         startToken
		self.EndToken =           None
		self.MultiPart =          False

	def __iter__(self):
		yield self.StartToken

	def __len__(self):
		return 0

	def __str__(self):
		return "[{0}]".format(self.__class__.__name__)


class EndOfBlock(Block):
	def __init__(self, endToken):
		self._previousBlock =     None
		self.NextBlock =          None
		self.StartToken =         None
		self.EndToken =           endToken
		self.MultiPart =          False

	def __iter__(self):
		yield self.EndToken

	def __len__(self):
		return 0

	def __str__(self):
		return "[{0}]".format(self.__class__.__name__)


class StartOfDocumentBlock(StartOfBlock, StartOfDocument):
	@classmethod
	def stateDocument(cls, parserState: ParserState):
		from pyVHDLParser.Blocks.Common     import IndentationBlock, WhitespaceBlock, LinebreakBlock
		from pyVHDLParser.Blocks.Reference  import Library, Use, Context
		from pyVHDLParser.Blocks.Sequential import Package
		from pyVHDLParser.Blocks.Structural import Entity, Architecture

		keywords = {
			# Keyword             Transition
			LibraryKeyword :      Library.LibraryBlock.stateLibraryKeyword,
			UseKeyword :          Use.UseBlock.stateUseKeyword,
		  ContextKeyword :      Context.NameBlock.stateContextKeyword,
		  EntityKeyword :       Entity.NameBlock.stateEntityKeyword,
		  ArchitectureKeyword : Architecture.NameBlock.stateArchitectureKeyword,
		  PackageKeyword :      Package.NameBlock.statePackageKeyword
		}

		token = parserState.Token
		if isinstance(token, SpaceToken):
			blockType =               IndentationBlock if isinstance(token, IndentationToken) else WhitespaceBlock
			parserState.NewBlock =    blockType(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, LinebreakToken):
			parserState.NewBlock =    LinebreakBlock(parserState.LastBlock, token)
			parserState.TokenMarker = None
			return
		elif isinstance(token, CommentToken):
			parserState.NewBlock =    CommentBlock(parserState.LastBlock, token)
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

		elif isinstance(token, EndOfDocumentToken):
			parserState.NewBlock =    EndOfDocumentBlock(token)
			return

		raise TokenParserException(
			"Expected one of these keywords: {keywords}. Found: '{tokenValue}'.".format(
				keywords=", ".join(
					[kw.__KEYWORD__.upper() for kw in keywords]
				),
				tokenValue=token.Value
			), token)


class EndOfDocumentBlock(EndOfBlock, EndOfDocument):        pass
class StartOfSnippetBlock(StartOfBlock, StartOfSnippet):    pass
class EndOfSnippetBlock(EndOfBlock, EndOfSnippet):          pass
