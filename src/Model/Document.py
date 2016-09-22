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
from src.Base               import ParserException
from src.Blocks.Reference           import Library, Use, Context
from src.Blocks.Structural          import Entity, Architecture, Component
from src.Blocks.Sequential          import Package, PackageBody
from src.Model.VHDLModel            import Document as DocumentModel
from src.Model.Reference            import Library as LibraryModel, Use as UseModel


class Document(DocumentModel):
	pass

	@classmethod
	def stateParse(cls, parserState):
		for block in parserState:
			if isinstance(block, Library.LibraryBlock):
				parserState.NextState = LibraryModel.stateParse
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
