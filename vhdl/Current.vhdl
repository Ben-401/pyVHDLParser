library IEEE;
use     IEEE.std_logic_vector.all;

-- This is the first package
-- described in two comment lines
entity system is
end entity;

architecture rtl of system is
begin
end architecture;

package pkg0 is
--	function func0 return integer;
end package;

package body pkg0 is
	constant const3 : std_logic := '0';
--	function func0 return integer is
--		constant const3 : std_logic := '0';
--
--		procedure proc1 is
--			variable var5 : integer := 20;
--			variable \var6\ : string := "20";
--		begin
--		end procedure proc1;
--	begin
--		report Patrick severity failure;
--	end function func0;
end package body;


context ctx is
	library OSVVM;
	use     OSVVM.Scoreborad.all;
end context;
