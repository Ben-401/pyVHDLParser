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
from typing                                         import List

from pyVHDLParser.Functions                         import Console
from pyVHDLParser.Token.Keywords                    import IdentifierToken
from pyVHDLParser.Blocks.Exception                  import BlockParserException
from pyVHDLParser.Blocks.List                       import GenericList as GenericListBlocks, PortList as PortListBlocks
from pyVHDLParser.Blocks.ObjectDeclaration.Constant import ConstantBlock
from pyVHDLParser.Blocks.Sequential                 import PackageBody as PackageBodyBlock
from pyVHDLParser.DocumentModel                     import DEBUG
from pyVHDLParser.DocumentModel.VHDLModel           import PackageBody as PackageBodyModel
from pyVHDLParser.DocumentModel.ObjectDeclaration   import Constant
from pyVHDLParser.DocumentModel.Reference           import Library, Use
from pyVHDLParser.DocumentModel.Parser              import BlockToModelParser

# Type alias for type hinting
ParserState = BlockToModelParser.BlockParserState


class PackageBody(PackageBodyModel):
	def __init__(self, packageBodyName):
		super().__init__()
		self._name = packageBodyName

	@classmethod
	def stateParse(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, PackageBodyBlock.NameBlock)
		cls.stateParsePackageBodyName(parserState)

		for block in parserState.BlockIterator:
			if isinstance(block, GenericListBlocks.OpenBlock):
				parserState.PushState = cls.stateParseGenericList
				parserState.ReIssue()
			elif isinstance(block, PortListBlocks.OpenBlock):
				parserState.PushState = cls.stateParsePortList
				parserState.ReIssue()
			elif isinstance(block, ConstantBlock):
				parserState.PushState = Constant.stateParse
				parserState.ReIssue()
			elif isinstance(block, PackageBodyBlock.EndBlock):
				break
		else:
			raise BlockParserException("", None)

		parserState.Pop()
		# parserState.CurrentBlock = None

	@classmethod
	def stateParsePackageBodyName(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, PackageBodyBlock.NameBlock)

		tokenIterator = iter(parserState)

		for token in tokenIterator:
			if isinstance(token, IdentifierToken):
				packageName = token.Value
				break
		else:
			raise BlockParserException("", None)

		oldNode = parserState.CurrentNode
		packageBody = cls(packageName)

		parserState.CurrentNode.AddPackageBody(packageBody)
		parserState.CurrentNode = packageBody
		parserState.CurrentNode.AddLibraries(oldNode.Libraries)
		parserState.CurrentNode.AddUses(oldNode.Uses)

		oldNode.Libraries.clear()
		oldNode.Uses.clear()

	@classmethod
	def stateParseGenericList(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, GenericListBlocks.OpenBlock)

		for block in parserState.BlockIterator:
			if isinstance(block, GenericListBlocks.ItemBlock):
				cls.stateParseGeneric(parserState)
			elif isinstance(block, GenericListBlocks.CloseBlock):
				break
		else:
			raise BlockParserException("", None)

		parserState.Pop()

	@classmethod
	def stateParseGeneric(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, GenericListBlocks.ItemBlock)

		tokenIterator = iter(parserState)

		for token in tokenIterator:
			if isinstance(token, IdentifierToken):
				genericName = token.Value
				break
		else:
			raise BlockParserException("", None)

		parserState.CurrentNode.AddGeneric(genericName)

	@classmethod
	def stateParsePortList(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, PortListBlocks.OpenBlock)

		for block in parserState.BlockIterator:
			if isinstance(block, PortListBlocks.ItemBlock):
				cls.stateParsePort(parserState)
			elif isinstance(block, PortListBlocks.CloseBlock):
				break
		else:
			raise BlockParserException("", None)

		parserState.Pop()

	@classmethod
	def stateParsePort(cls, parserState: ParserState):
		assert isinstance(parserState.CurrentBlock, PortListBlocks.ItemBlock)

		tokenIterator = iter(parserState)

		for token in tokenIterator:
			if isinstance(token, IdentifierToken):
				portName = token.Value
				break
		else:
			raise BlockParserException("", None)

		parserState.CurrentNode.AddPort(portName)

	def AddLibraries(self, libraries : List[Library]):
		if ((DEBUG is True) and (len(libraries) > 0)): print("{DARK_CYAN}Adding libraries to package body {GREEN}{0}{NOCOLOR}:".format(self._name, **Console.Foreground))
		for library in libraries:
			if DEBUG: print("  {GREEN}{0!s}{NOCOLOR}".format(library, **Console.Foreground))
			self._libraries.append(library._library)

	def AddUses(self, uses : List[Use]):
		if ((DEBUG is True) and (len(uses) > 0)): print("{DARK_CYAN}Adding uses to package body {GREEN}{0}{NOCOLOR}:".format(self._name, **Console.Foreground))
		for use in uses:
			if DEBUG: print("  {GREEN}{0!s}{NOCOLOR}".format(use, **Console.Foreground))
			self._uses.append(use)

	def AddConstant(self, constant):
		if DEBUG: print("{DARK_CYAN}Adding constant to package body {GREEN}{0}{NOCOLOR}:\n  {1!s}".format(self._name, constant, **Console.Foreground))
		self._declaredItems.append(constant)

	def Print(self, indent=0):
		indentation = "  "*indent
		for lib in self._libraries:
			print("{indent}{DARK_CYAN}LIBRARY{NOCOLOR} {GREEN}{lib}{NOCOLOR};".format(indent=indentation, lib=lib, **Console.Foreground))
		for lib, pack, obj in self._uses:
			print("{indent}{DARK_CYAN}USE {GREEN}{lib}{NOCOLOR}.{GREEN}{pack}{NOCOLOR}.{GREEN}{obj}{NOCOLOR};".format(indent=indentation, lib=lib, pack=pack, obj=obj, **Console.Foreground))
		print()
		print("{indent}{DARK_CYAN}PACKAGE BODY{NOCOLOR} {GREEN}{name}{NOCOLOR} {DARK_CYAN}IS{NOCOLOR}".format(indent=indentation, name=self._name, **Console.Foreground))
		if (len(self._declaredItems) > 0):
			for item in self._declaredItems:
				item.Print(indent+1)
		print("{indent}{DARK_CYAN}END PACKAGE BODY{NOCOLOR};".format(indent=indentation, name=self._name, **Console.Foreground))

