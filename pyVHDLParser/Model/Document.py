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
from pyVHDLParser.Base               import ParserException
from pyVHDLParser.Blocks.Reference  import Library, Use, Context
from pyVHDLParser.Blocks.Structural import Entity, Architecture, Component
from pyVHDLParser.Blocks.Sequential import Package, PackageBody
from pyVHDLParser.Model.VHDLModel   import Document as DocumentModel
from pyVHDLParser.Model.Reference   import Library as LibraryModel, Use as UseModel
from pyVHDLParser.Model.Parser      import BlockToModelParser

# Type alias for type hinting
ParserState = BlockToModelParser.BlockParserState


class Document(DocumentModel):
	def __init__(self):
		self.__libraries = []
		self.__uses =      []

	@classmethod
	def stateParse(cls, parserState: ParserState):
		block = parserState.CurrentBlock
		if isinstance(block, Library.LibraryBlock):
			parserState.PushState = LibraryModel.Library.stateParse
		elif isinstance(block, Use.UseBlock):
			pass
		elif isinstance(block, Entity.NameBlock):
			pass
		elif isinstance(block, Architecture.NameBlock):
			pass
		elif isinstance(block, Package.NameBlock):
			pass
		elif isinstance(block, PackageBody.NameBlock):
			pass
		else:
			parserState.CurrentBlock = next(parserState.BlockIterator)

	def AddLibrary(self, libraryName):
		self.__libraries.append(libraryName)

	def AddUse(self, libraryName, packageName, objectName):
		self.__uses.append((libraryName, packageName, objectName))
