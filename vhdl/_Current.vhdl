entity system is
	generic (
		constant WIDTH : in natural;
		HEIGHT1 : natural := xyz;
		HEIGHT2 : natural := 19324 + abc;
		HEIGHT3 : natural := 678 * 453;
		DEPTH : natural := (345 / 666) <= func
	);
	port (
		Clock : bit := '1';
		Reset : std_logic := "011101"
	);
end entity;

xxx

architecture rtl of system is
begin
	process (Clock, Reset)
		variable halt : bit;
	begin
	end process;
end architecture;

context ctx is
	library OSVVM;
	use     OSVVM.Scoreborad.all;
end context;

library IEEE;
use     IEEE.std_logic_vector.all;

package pkg0 is
	function func0 return integer;
end package;

package body pkg0 is
	constant const3 : std_logic := '0';
	function func1 return integer is
		constant const3 : std_logic := '0';
		/*procedure proc1 is
			variable var5 : integer := 20;
			variable \var6\ : string := "20";
		begin
		end procedure proc1;*/
	begin
		report Patrick severity failure;
	end function func0;
end package body;
