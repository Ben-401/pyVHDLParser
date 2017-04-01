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
from pathlib import Path

import sys
from textwrap import dedent

from pyVHDLParser.Base               import ParserException
from pyVHDLParser.Functions          import Console, Exit
from pyVHDLParser.Token import StartOfDocumentToken, EndOfDocumentToken, CharacterToken, SpaceToken, StringToken, \
	LinebreakToken, CommentToken, IndentationToken, Token
from pyVHDLParser.Token.Keywords import BoundaryToken, EndToken, KeywordToken, DelimiterToken, IdentifierToken
from pyVHDLParser.Token.Parser       import Tokenizer
from pyVHDLParser.Blocks import CommentBlock, Block
from pyVHDLParser.Blocks.Common      import LinebreakBlock, IndentationBlock
from pyVHDLParser.Blocks.Document    import StartOfDocumentBlock, EndOfDocumentBlock
from pyVHDLParser.Blocks.Structural  import Entity
from pyVHDLParser.Blocks.List        import GenericList, PortList
from pyVHDLParser.Blocks.Parser      import TokenToBlockParser
from pyVHDLParser.Groups             import BlockToGroupParser
from pyVHDLParser.DocumentModel.Document import Document
from pyVHDLParser.DocumentModel.Parser import GroupToModelParser


Console.init()

rootDirectory = Path(".")
vhdlDirectory = rootDirectory / "vhdl"

if (len(sys.argv) == 2):
	file = Path(sys.argv[1])
	mode = 255
elif (len(sys.argv) == 3):
	file = Path(sys.argv[1])
	mode = int(sys.argv[2])
	print("mode={0}".format(mode))
else:
	print("File name expected.")
	Exit.exit(-1)

if (not file.exists()):
	print("File '{0!s}' does not exist.".format(file))

with file.open('r') as fileHandle:
	content = fileHandle.read()


# ==============================================================================
if (mode & 6 == 2):
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = Tokenizer.GetWordTokenizer(content)

	try:
		for vhdlToken in wordTokenStream:
			if isinstance(vhdlToken, (LinebreakToken, SpaceToken, IndentationToken)):
				print("{DARK_GRAY}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
			elif isinstance(vhdlToken, CommentToken):
				print("{DARK_GREEN}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
			elif isinstance(vhdlToken, CharacterToken):
				print("{DARK_CYAN}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
			elif isinstance(vhdlToken, StringToken):
				print("{WHITE}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
			elif isinstance(vhdlToken, (StartOfDocumentToken, EndOfDocumentToken)):
				print("{YELLOW}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
			else:
				print("{RED}{block}{NOCOLOR}".format(block=vhdlToken, **Console.Foreground))
	except ParserException as ex:
		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	except NotImplementedError as ex:
		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))

	if (mode & 1 == 1):
		print("{RED}{line}{NOCOLOR}".format(line="=" * 160, **Console.Foreground))
		wordTokenStream = Tokenizer.GetWordTokenizer(content)

		try:
			tokenIterator = iter(wordTokenStream)
			firstToken = next(tokenIterator)
			if (not isinstance(firstToken, StartOfDocumentToken)):
				print("{RED}First block is not StartOfDocumentToken: {token}{NOCOLOR}".format(token=firstToken, **Console.Foreground))

			lastToken = None
			vhdlToken = firstToken

			for newToken in tokenIterator:
				if (vhdlToken.NextToken is None):
					print("{RED}Token has an open end.{NOCOLOR}".format(**Console.Foreground))
					print("{RED}  Token:  {token}{NOCOLOR}".format(token=vhdlToken, **Console.Foreground))
				elif ((vhdlToken is not firstToken) and (lastToken.NextToken is not vhdlToken)):
					print("{RED}Last token is not connected to the current token.{NOCOLOR}".format(**Console.Foreground))
					print("{RED}  Curr:   {token}{NOCOLOR}".format(token=vhdlToken, **Console.Foreground))
					print("{DARK_RED}    Prev: {token}{NOCOLOR}".format(token=vhdlToken.PreviousToken, **Console.Foreground))
					print("{RED}  Last:   {token}{NOCOLOR}".format(token=lastToken, **Console.Foreground))
					print("{RED}    Next: {token}{NOCOLOR}".format(token=lastToken.NextToken, **Console.Foreground))
					if (lastToken.NextToken is None):
						print("{DARK_RED}    Next: {token}{NOCOLOR}".format(token="--------", **Console.Foreground))
					else:
						print("{DARK_RED}    Next: {token}{NOCOLOR}".format(token=lastToken.NextToken.NextToken, **Console.Foreground))
					if (vhdlToken.PreviousToken is None):
						print("{DARK_RED}    Prev: {token}{NOCOLOR}".format(token="--------", **Console.Foreground))
					else:
						print("{DARK_RED}    Prev: {token}{NOCOLOR}".format(token=vhdlToken.PreviousToken.PreviousToken, **Console.Foreground))
				elif (vhdlToken.PreviousToken is not lastToken):
					print("{RED}Current token is not connected to lastToken.{NOCOLOR}".format(**Console.Foreground))
					print("{RED}  Curr:   {token}{NOCOLOR}".format(token=vhdlToken, **Console.Foreground))
					print("{RED}    Prev: {token}{NOCOLOR}".format(token=vhdlToken.PreviousToken, **Console.Foreground))
					print("{RED}  Last:   {token}{NOCOLOR}".format(token=lastToken, **Console.Foreground))
					print("{DARK_RED}    Next: {token}{NOCOLOR}".format(token=lastToken.NextToken, **Console.Foreground))

				lastToken = vhdlToken
				vhdlToken = newToken

				if isinstance(newToken, EndOfDocumentToken):
					break
			else:
				print("{RED}No EndOfDocumentToken found.{NOCOLOR}".format(**Console.Foreground))

			if (not isinstance(vhdlToken, EndOfDocumentToken)):
				print("{RED}Last token is not EndOfDocumentToken: {token}{NOCOLOR}".format(token=lastToken, **Console.Foreground))
			elif (vhdlToken.PreviousToken is not lastToken):
				print("{RED}EndOfDocumentToken is not connected to lastToken.{NOCOLOR}".format(**Console.Foreground))
				print("{RED}  Curr:   {token}{NOCOLOR}".format(token=vhdlToken, **Console.Foreground))
				print("{RED}    Prev: {token}{NOCOLOR}".format(token=vhdlToken.PreviousToken, **Console.Foreground))
				print("{RED}  Last:   {token}{NOCOLOR}".format(token=lastToken, **Console.Foreground))
				print("{DARK_RED}    Next: {token}{NOCOLOR}".format(token=lastToken.NextToken, **Console.Foreground))

		except ParserException as ex:
			print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
		except NotImplementedError as ex:
			print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))

# ==============================================================================
if (mode & 6 == 4):
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = Tokenizer.GetWordTokenizer(content)
	vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream, debug=(mode & 1 == 1))

	try:
		for vhdlBlock in vhdlBlockStream:
			if isinstance(vhdlBlock, (LinebreakBlock, IndentationBlock)):
				print("{DARK_GRAY}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			elif isinstance(vhdlBlock, CommentBlock):
				print("{DARK_GREEN}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			elif isinstance(vhdlBlock, (Entity.NameBlock, Entity.NameBlock, Entity.EndBlock)):
				print("{DARK_RED}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			elif isinstance(vhdlBlock, (GenericList.OpenBlock, GenericList.DelimiterBlock, GenericList.CloseBlock)):
				print("{DARK_BLUE}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			elif isinstance(vhdlBlock, (PortList.OpenBlock, PortList.DelimiterBlock, PortList.CloseBlock)):
				print("{DARK_CYAN}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			elif isinstance(vhdlBlock, (GenericList.ItemBlock, PortList.ItemBlock)):
				print("{BLUE}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			else:
				print("{YELLOW}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))

	except ParserException as ex:
		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	except NotImplementedError as ex:
		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))

if (mode & 6 == 6):
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = Tokenizer.GetWordTokenizer(content)
	vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream, debug=(mode & 1 == 1))

	graphML = []
	graphML.append(dedent("""\
		<?xml version="1.0" encoding="UTF-8"?>
		<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
			xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java"
			xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0"
			xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0"
			xmlns:y="http://www.yworks.com/xml/graphml"
			xmlns:yed="http://www.yworks.com/xml/yed/3"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
			<!--Created by yEd 3.16.2.1-->
		  <key for="port" id="d0" yfiles.type="portgraphics"/>
		  <key for="port" id="d1" yfiles.type="portgeometry"/>
		  <key for="port" id="d2" yfiles.type="portuserdata"/>
		  <key attr.name="url" attr.type="string" for="node" id="d3"/>
		  <key attr.name="description" attr.type="string" for="node" id="d4"/>
		  <key for="node" id="d5" yfiles.type="nodegraphics"/>
		  <key for="graphml" id="d6" yfiles.type="resources"/>
		  <key attr.name="url" attr.type="string" for="edge" id="d7"/>
		  <key attr.name="description" attr.type="string" for="edge" id="d8"/>
		  <key for="edge" id="d9" yfiles.type="edgegraphics"/>
			<graph id="Current.vhdl" edgedefault="directed">
				<node id="n0">
		      <data key="d5">
		        <y:ShapeNode>
		          <y:Geometry height="25.0" width="300.0" />
		          <y:Fill color="#FF0000" transparent="false"/>
		          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
		          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">Forward Edge Error</y:NodeLabel>
		          <y:Shape type="rectangle"/>
		        </y:ShapeNode>
		      </data>
		    </node>
				<node id="n1">
		      <data key="d5">
		        <y:ShapeNode>
		          <y:Geometry height="25.0" width="300.0" />
		          <y:Fill color="#FF0000" transparent="false"/>
		          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
		          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">Backward Edge Error</y:NodeLabel>
		          <y:Shape type="rectangle"/>
		        </y:ShapeNode>
		      </data>
		    </node>
				<node id="n2">
		      <data key="d5">
		        <y:ShapeNode>
		          <y:Geometry height="25.0" width="300.0" />
		          <y:Fill color="#CC99FF" transparent="false"/>
		          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
		          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">StartOfDocumentBlock</y:NodeLabel>
		          <y:Shape type="rectangle"/>
		        </y:ShapeNode>
		      </data>
		    </node>
				<node id="n3">
		      <data key="d5">
		        <y:ShapeNode>
		          <y:Geometry height="25.0" width="300.0" />
		          <y:Fill color="#CC99FF" transparent="false"/>
		          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
		          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">StartOfDocumentToken</y:NodeLabel>
		          <y:Shape type="rectangle"/>
		        </y:ShapeNode>
		      </data>
		    </node>
		    <edge source="n2" target="n3">
		      <data key="d9">
		        <y:PolyLineEdge>
		          <y:LineStyle color="#000000" type="dashed" width="1.0"/>
		          <y:Arrows source="none" target="delta"/>
		          <y:BendStyle smoothed="false"/>
		        </y:PolyLineEdge>
		      </data>
		    </edge>
		"""))

	try:
		blockIterator = iter(vhdlBlockStream)
		firstBlock = next(blockIterator)
		if (not isinstance(firstBlock, StartOfDocumentBlock)):
			print("{RED}First block is not StartOfDocumentBlock: {block}{NOCOLOR}".format(block=firstBlock, **Console.Foreground))
		elif (not isinstance(firstBlock.StartToken, StartOfDocumentToken)):
			print("{RED}First block is not StartOfDocumentToken: {token}{NOCOLOR}".format(token=firstBlock.StartToken, **Console.Foreground))

		lastBlock : Block = firstBlock
		endBlock  : Block = None
		lastToken : Token = firstBlock.StartToken

		blockRegister = {firstBlock: "n2"}
		tokenRegister = {firstBlock.StartToken: "n3"}

		blockID = 3
		for vhdlBlock in blockIterator:
			blockID += 1
			nodeID = "n" + str(blockID)
			blockRegister[vhdlBlock] = nodeID

			graphML.append(dedent("""\
						<node id="{id}">
				      <data key="d5">
				        <y:ShapeNode>
				          <y:Geometry height="25.0" width="300.0" />
				          <y:Fill color="#CCFFCC" transparent="false"/>
				          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
				          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">{label}</y:NodeLabel>
				          <y:Shape type="rectangle"/>
				        </y:ShapeNode>
				      </data>
				    </node>
						<edge source="{src1}" target="{tar1}">
				      <data key="d9">
				        <y:PolyLineEdge>
				          <y:LineStyle color="#000000" type="line" width="1.0"/>
				          <y:Arrows source="none" target="delta"/>
				          <y:BendStyle smoothed="false"/>
				        </y:PolyLineEdge>
				      </data>
				    </edge>
						<edge source="{src2}" target="{tar2}">
				      <data key="d9">
				        <y:PolyLineEdge>
				          <y:LineStyle color="#000000" type="line" width="1.0"/>
				          <y:Arrows source="none" target="delta"/>
				          <y:BendStyle smoothed="false"/>
				        </y:PolyLineEdge>
				      </data>
				    </edge>
				""".format(
					id=nodeID,
					label="{classname} at ({line1}:{col1}) .. ({line2}:{col2})".format(
						classname=vhdlBlock.__class__.__qualname__,
						line1=vhdlBlock.StartToken.Start.Row,
						col1=vhdlBlock.StartToken.Start.Column,
						line2="xx",#vhdlBlock.EndToken.End.Row,
						col2="yy" #vhdlBlock.EndToken.End.Column
					),# "IdentifierToken 'myPackage' (37:12)"
			    src1=blockRegister[lastBlock],
			    tar1=blockRegister.get(lastBlock.NextBlock, "n0"),
					src2=nodeID,
					tar2=blockRegister.get(vhdlBlock, "n1")
			  )
			))


			if isinstance(vhdlBlock, EndOfDocumentBlock):
				endBlock = vhdlBlock
				break
			tokenIterator = iter(vhdlBlock)

			for token in tokenIterator:
				blockID += 1
				nodeID = "n" + str(blockID)
				tokenRegister[token] = nodeID
				graphML.append(dedent("""\
							<node id="{id}">
					      <data key="d5">
					        <y:ShapeNode>
					          <y:Geometry height="25.0" width="300.0" />
					          <y:Fill color="#CCCCCC" transparent="false"/>
					          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
					          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">{label}</y:NodeLabel>
					          <y:Shape type="rectangle"/>
					        </y:ShapeNode>
					      </data>
					    </node>
							<edge source="{src1}" target="{tar1}">
					      <data key="d9">
					        <y:PolyLineEdge>
					          <y:LineStyle color="#000000" type="line" width="1.0"/>
					          <y:Arrows source="none" target="delta"/>
					          <y:BendStyle smoothed="false"/>
					        </y:PolyLineEdge>
					      </data>
					    </edge>
							<edge source="{src2}" target="{tar2}">
					      <data key="d9">
					        <y:PolyLineEdge>
					          <y:LineStyle color="#000000" type="line" width="1.0"/>
					          <y:Arrows source="none" target="delta"/>
					          <y:BendStyle smoothed="false"/>
					        </y:PolyLineEdge>
					      </data>
					    </edge>
					""".format(
					id=nodeID,
					label="{classname} at ({line1}:{col1}) .. ({line2}:{col2})".format(
						classname=token.__class__.__qualname__,
						line1=token.Start.Row,
						col1=token.Start.Column,
						line2=token.End.Row,
						col2=token.End.Column
					),  # "IdentifierToken 'myPackage' (37:12)"
					src1=tokenRegister[lastToken],
					tar1=tokenRegister.get(lastToken.NextToken, "n0"),
					src2=nodeID,
					tar2=tokenRegister.get(token.PreviousToken, "n1")
				)
				))


				if (token.NextToken is None):
					print("{RED}Token has an open end.{NOCOLOR}".format(**Console.Foreground))
					print("{RED}  Block:  {block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
					print("{RED}  Token:  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				elif (lastToken.NextToken is not token):
					print("{RED}Last token is not connected to the current one.{NOCOLOR}".format(**Console.Foreground))
					token11 = lastToken
					token12 = "--------" if (token.PreviousToken is None) else token.PreviousToken.PreviousToken
					token21 = lastToken.NextToken
					token22 = token.PreviousToken
					token31 = "--------" if (lastToken.NextToken is None) else lastToken.NextToken.NextToken
					token32 = token
					print("{RED} Block: {block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
					print("{RED} | Last:  {token1}{NOCOLOR} =?= {DARK_RED}Prev: {token2}{NOCOLOR}".format(token1=token11, token2=token12, **Console.Foreground))
					print("{DARK_RED} |  Next: {token1}{NOCOLOR} =?= {DARK_RED}Prev: {token2}{NOCOLOR}".format(token1=token21, token2=token22, **Console.Foreground))
					print("{DARK_RED} v  Next: {token1}{NOCOLOR} =?= {RED}Curr: {token2}{NOCOLOR}".format(token1=token31, token2=token32, **Console.Foreground))
				elif (token.PreviousToken is not lastToken):
					print("{RED}Current token is not connected to lastToken.{NOCOLOR}".format(**Console.Foreground))
					print("{RED}  Block:  {block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
					print("{RED}  Last:   {token}{NOCOLOR}".format(token=lastToken, **Console.Foreground))
					print("{DARK_RED}    Next: {token}{NOCOLOR}".format(token=lastToken.NextToken, **Console.Foreground))
					print("{RED}  Curr:   {token}{NOCOLOR}".format(token=token, **Console.Foreground))
					print("{RED}    Prev: {token}{NOCOLOR}".format(token=token.PreviousToken, **Console.Foreground))

				lastToken = token

			lastBlock = vhdlBlock
		else:
			print("{RED}No EndOfDocumentBlock found.{NOCOLOR}".format(**Console.Foreground))

		if (not isinstance(endBlock, EndOfDocumentBlock)):
			print("{RED}Last block is not EndOfDocumentBlock: {block}{NOCOLOR}".format(block=endBlock, **Console.Foreground))
		elif (not isinstance(endBlock.StartToken, EndOfDocumentToken)):
			print("{RED}Last token is not EndOfDocumentToken: {token}{NOCOLOR}".format(token=endBlock.StartToken, **Console.Foreground))

		blockID += 1
		nodeID = "n" + str(blockID)
		tokenRegister[lastBlock.StartToken] = nodeID
		graphML.append(dedent("""\
					<node id="{id}">
			      <data key="d5">
			        <y:ShapeNode>
			          <y:Geometry height="25.0" width="300.0" />
			          <y:Fill color="#CC99FF" transparent="false"/>
			          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
			          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="l" textColor="#000000" verticalTextPosition="bottom" visible="true" width="195.34375" x="4.0" y="3.1494140625">{label}</y:NodeLabel>
			          <y:Shape type="rectangle"/>
			        </y:ShapeNode>
			      </data>
			    </node>
					<edge source="{src1}" target="{tar1}" />
					<edge source="{src2}" target="{tar2}" />
			""".format(
			id=nodeID,
			label="{classname} at ({line1}:{col1}) .. ({line2}:{col2})".format(
				classname=EndOfDocumentToken.__qualname__,
				line1=lastBlock.StartToken.Start.Row,
				col1=lastBlock.StartToken.Start.Column,
				line2=lastBlock.StartToken.End.Row,
				col2=lastBlock.StartToken.End.Column
			),  # "IdentifierToken 'myPackage' (37:12)"
			src1=tokenRegister[lastToken],
			tar1=tokenRegister.get(lastToken.NextToken, "n0"),
			src2=nodeID,
			tar2=tokenRegister.get(endBlock.PreviousBlock, "n1")
		)
		))

	except ParserException as ex:
		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	except NotImplementedError as ex:
		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	finally:
		graphML.append(dedent("""\
				</graph>
			</graphml>
			"""))

	with file.with_suffix(".graphml").open('w') as fileHandle:
		fileHandle.write("".join(graphML))

# ==============================================================================
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = Tokenizer.GetWordTokenizer(content)
	vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream, debug=(mode & 1 == 1))

	try:
		for vhdlBlock in vhdlBlockStream:
			print("{YELLOW}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
			for token in vhdlBlock:
				if isinstance(token, (IndentationToken, LinebreakToken, BoundaryToken, DelimiterToken, EndToken)):
					print("{DARK_GRAY}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				elif isinstance(token, (CommentToken)):
					print("{DARK_GREEN}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				elif isinstance(token, KeywordToken):
					print("{DARK_CYAN}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				elif isinstance(token, (StringToken, CharacterToken)):
					print("{DARK_GREEN}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				elif isinstance(token, (IdentifierToken)):
					print("{GREEN}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))
				else:
					print("{RED}  {token}{NOCOLOR}".format(token=token, **Console.Foreground))

	except ParserException as ex:
		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	except NotImplementedError as ex:
		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))


# ==============================================================================
if (mode & 8 == 8):
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = [token for token in Tokenizer.GetWordTokenizer(content)]
	vhdlBlockStream = [block for block in TokenToBlockParser.Transform(wordTokenStream)]
	vhdlGroupStream = BlockToGroupParser.Transform(vhdlBlockStream, debug=(mode & 1 == 1))

	try:
		for vhdlGroup in vhdlGroupStream:
			print("{CYAN}{block}{NOCOLOR}".format(block=vhdlGroup, **Console.Foreground))
			for block in vhdlGroup:
				if isinstance(block, (IndentationToken, LinebreakToken, BoundaryToken, DelimiterToken, EndToken)):
					print("{DARK_GRAY}  {block}{NOCOLOR}".format(block=block, **Console.Foreground))
				elif isinstance(block, (CommentToken)):
					print("{DARK_GREEN}  {block}{NOCOLOR}".format(block=block, **Console.Foreground))
				elif isinstance(block, KeywordToken):
					print("{DARK_CYAN}  {block}{NOCOLOR}".format(block=block, **Console.Foreground))
				elif isinstance(block, (StringToken, SpaceToken, CharacterToken)):
					print("{DARK_GREEN}  {block}{NOCOLOR}".format(block=block, **Console.Foreground))
				else:
					print("{YELLOW}  {block}{NOCOLOR}".format(block=block, **Console.Foreground))

	except ParserException as ex:
		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
	except NotImplementedError as ex:
		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))

# ==============================================================================
# if (mode & 16 == 16):
# 	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
# 	wordTokenStream = Tokenizer.GetWordTokenizer(content)
# 	vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream, debug=(mode & 1 == 1))
# 	strippedBlockStream = StripAndFuse(vhdlBlockStream)
#
# 	try:
# 		for vhdlBlock in strippedBlockStream:
# 			if isinstance(vhdlBlock, (LinebreakBlock, IndentationBlock)):
# 				print("{DARK_GRAY}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			elif isinstance(vhdlBlock, CommentBlock):
# 				print("{DARK_GREEN}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			elif isinstance(vhdlBlock, (Entity.NameBlock, Entity.ConcurrentBeginBlock, Entity.EndBlock)):
# 				print("{DARK_RED}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			elif isinstance(vhdlBlock, (GenericList.OpenBlock, GenericList.DelimiterBlock, GenericList.CloseBlock)):
# 				print("{DARK_BLUE}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			elif isinstance(vhdlBlock, (PortList.OpenBlock, PortList.DelimiterBlock, PortList.CloseBlock)):
# 				print("{DARK_CYAN}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			elif isinstance(vhdlBlock, (GenericList.ItemBlock, PortList.ItemBlock)):
# 				print("{BLUE}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
# 			else:
# 				print("{YELLOW}{block}{NOCOLOR}".format(block=vhdlBlock, **Console.Foreground))
#
# 	except ParserException as ex:
# 		print("{RED}ERROR: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))
# 	except NotImplementedError as ex:
# 		print("{RED}NotImplementedError: {0!s}{NOCOLOR}".format(ex, **Console.Foreground))


if (mode & 32 == 32):
	print("{RED}{line}{NOCOLOR}".format(line="="*160, **Console.Foreground))
	wordTokenStream = Tokenizer.GetWordTokenizer(content)
	vhdlBlockStream = TokenToBlockParser.Transform(wordTokenStream, debug=(mode & 1 == 1))
	vhdlGroupStream = BlockToGroupParser.Transform(vhdlBlockStream, debug=(mode & 1 == 1))

	document = Document()
	GroupToModelParser.Transform(document, vhdlGroupStream, debug=True)

	document.Print(0)
