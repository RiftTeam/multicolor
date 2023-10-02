-- title:  Display
-- author: Mantratronic/Rift
-- desc:   show a mulTIColor image
-- script: lua

-- CODEBLOCK

function setPalette(p)
	for i=0,15 do
		for j=0,2 do
			poke(0x03FC0 + (i*3) + j,p[(i*3) + j+1])
		end
	end
end

--- high colour image test
hci_numpals = 0
hci_lp={}
hci_width = 0
hci_height = 0
hci_data={}
hci_image=""
function hci_init()
	local tnb=tonumber
	local i =0
	-- load palettes
	hci_numpals = #pal/96 -- pal length / 2 characters * 3 RGB * 16 colours = 96
	for i=1,hci_numpals do
		currentIP = {} 
		for j=0,47 do
			x=(i-1)*96 + j*2 + 1
			c1 = tnb(pal:sub(x,x),16)
			c2 = tnb(pal:sub(x+1,x+1),16)
			c = c2+16*c1
			table.insert(currentIP,c)	
		end
		table.insert(hci_lp,currentIP)
	end

	-- load image
	local width = #gfx / hci_numpals
	local height = hci_numpals
	trace("width x height:"..width.."x"..height)
    hci_width = width
    hci_height = height

	if width <= 128 and height <= 128 then
	
		for i=0,width*height do
            local x = i%width
            local y = i//width
			c= tnb(gfx:sub(i+1,i+1),16)
            poke4(0x8000 + (((x//8+y//8*16)*32)*2+(x%8)+(y%8)*8),c)
		end
	elseif width <=128 and height > 128 then
    	-- if height > 128 (same as above, just fills spritesheet too)
        local addr = 0x8000
		
		for i=0,width*height do
            local x = i%width
            local y = i//width
			c= tnb(gfx:sub(i+1,i+1),16)
            poke4(addr + (((x//8+y//8*16)*32)*2+(x%8)+(y%8)*8),c)
		end
	elseif width >128 and height <= 128 then
	    -- if width > 128, stores rightmost pixels in spritesheet
        local addr = 0x8000
        local offset = 0
		
		for i=0,width*height do
            local x = i%width
            local y = i//width
			c= tnb(gfx:sub(i+1,i+1),16)

            if x >= 128 then
                offset = 0x4000
                x = x-128
            else
                offset = 0
            end
            poke4(addr + offset + (((x//8+y//8*16)*32)*2+(x%8)+(y%8)*8),c)
		end
	elseif width >128 and height > 128 then
		-- if both are bigger
		-- load 128 x 128 in the tilesheet
		
        local addr = 0x8000
        local offset = 0
		for i=0,width*height do
            local x = i%width
            local y = i//width
			c= tnb(gfx:sub(i+1,i+1),16)

            if y >= 128 then
                offset = 0x4000
                local leftover = 128 -(width-128)
                y = y-128 + 8 * (x // leftover)
                x = (x % leftover) + (width-128)
            elseif x >= 128 then
                offset = 0x4000
                x = x-128
            else
                offset = 0
            end
            poke4(addr + offset + (((x//8+y//8*16)*32)*2+(x%8)+(y%8)*8),c)
		end
	end
    sync(0,0,true)
end
function hci_update(ft)
	-- load palettes into currentLP
	currentLP={}
	for i=0,135 do
		table.insert(currentLP,hci_lp[i+ 1])
	end
end
function hci_draw(ft)
	-- switch to correct bank etc
	-- draw sprites
	cls(0)

    if hci_width <=128 and hci_height <=128 then
        spr(0,hci_width,0,-1,1,0,0,hci_width//8,hci_height//8)
        -- pixel by pixel
        for i=0,hci_width*hci_height-1 do
            c= tonumber(gfx:sub(i+1,i+1),16)
            pix(i%hci_width,i//hci_width,c)
        end
    elseif hci_width <=128 and hci_height > 128 then
        -- if height > 128 (same as above, just copies from spritesheet too)
        spr(0,hci_width,0,-1,1,0,0,hci_width//8,16)
        spr(256,hci_width,128,-1,1,0,0,hci_width//8,hci_height//8-16)
        -- pixel by pixel
        for i=0,hci_width*hci_height-1 do
            c= tonumber(gfx:sub(i+1,i+1),16)
            pix(i%hci_width,i//hci_width,c)
        end
    elseif hci_width >128 and hci_height <= 128 then
        -- if width > 128
	    -- reads rightmost pixels from spritesheet
        spr(0,0,0,-1,1,0,0,16,hci_height//8)
        spr(256,128,0,-1,1,0,0,hci_width//8-16,hci_height//8)
        --[[ pixel by pixel
        for i=0,hci_width*hci_height-1 do
            c= tonumber(gfx:sub(i+1,i+1),16)
            pix(i%hci_width,i//hci_width,c)
        end
        --]]
    elseif hci_width >128 and hci_height > 128 then
        -- if both > 128
        spr(0,0,0,-1,1,0,0,16,16)
	    -- reads rightmost pixels from spritesheet
        spr(256,128,0,-1,1,0,0,hci_width//8-16,16)
        -- reads leftovers
        local normal_width = (hci_width//8)
        local leftover_width = (32-hci_width//8)
        for level=0,normal_width/leftover_width do
            spr(256+normal_width-16 + level*16, level*leftover_width*8,128,-1,1,0,0,leftover_width,1)
        end
    end

	-- make sure active scan is on
	activeScan=1
end

--- high colour effect test
hce_palettes={}
function hce_init()
	for i=0,20 do
		hce_palettes[i] = mixPalette2(palettes[3],aqua,i/20)
		--table.insert(hce_palettes,mixPalette(gray,aqua,i/20))
	end
end
function hce_update(ft)
	currentLP={}
	hce_palettes={}
	for i=0,20 do
		hce_palettes[i] = mixPalette2(palettes[6],aqua,i/20)
		--table.insert(hce_palettes,mixPalette(gray,aqua,i/20))
	end
	for i=0,135 do
		--[[
		if (i)//1%3 == 1 then
			table.insert(currentLP,palettes[1])
		else
			table.insert(currentLP,palettes[2])
		end--]]
		table.insert(currentLP,hce_palettes[(i+ft)//4%#hce_palettes])
		table.insert(currentLP,hce_palettes[(i+ft)//4%#hce_palettes])
	end
end
function hce_draw(ft)
	-- switch to the right bank, should probably only happen on scene switch
	sync(35,1,false)
	spr(0,0,0,-1,1,0,0,16,16)
	spr(256,128,1,-1,1,0,0,16,16)
	activeScan=1
	poke(0x3ff8,4)
end

activeScan=1
currentP={}
currentLP={}
function SCN(l)
	if activeScan == 1 then
		--[[]
		for i=0,47 do
			poke(0x03FC0 + i,(i*l)%255)
		end --]]
		setPalette(currentLP[(l%#currentLP)+1])
	elseif (l==0) then
		setPalette(currentP)
	end
end

hci_init()
function TIC()
--trace("pal length:"..(#pal/(6*16)).." | gfx length:"..(#gfx/240))
hci_update(1)
hci_draw(1)
end