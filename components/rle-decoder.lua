-- title:  RLE Decoder
-- author: Decca/Rift
-- desc:   decode rle to global var
-- script: lua

-- DESCRIPTION
--
-- store pixel values (colors) as rle-encoded string
--  format: <rle-encoded colorvalues>
--     rle: colorvalues in uppercase letters - A=0,B=1...P=15
--          repeat of values in digits - 0...9
--          easier decoding using different symbols for values vs. repeats
--          a single value has no repeat-digit: A
--          two same values have no repeat-digit, just double letters: AA
--          three or more same values are appended with repeat-digits: A2
--          three: the letter itself and two additional repeats: A2 > AAA
--          seven: the letter itself and six additional repeats: A6 > AAAAAAA
local rle = "MK4M3PMMKKM2NMMCFM2KMMEPM2PMMKKMMK4M3KM4AK2AM2"

-- CODEBLOCK

-- the rle-decoder
function togfx(str)
  local d = "" -- (d)ecoded data
  for m, c in str:gmatch("(%u+)([^%u]+)") do -- decode rle, (m)atch & (c)ounter
    d = d .. m .. (m:sub(-1):rep(c))
  end
  _G.gfx = "" -- global graphic variable
  for v = 1,#d,1 do
    gfx = gfx .. string.format("%x",string.byte(d:sub(v,v))-65) -- get (c)olor value in hex
  end
end

-- call the decoder
togfx(rle)
