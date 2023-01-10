-- title:  Display31
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
hci_lop={}
hci_width = 0
hci_height = 0
hci_data={}
hci_image=""
function hci_init()
	local tnb=tonumber
	local i =0
	-- load palettes
	hci_numpals = #pal/186 -- pal length / 2 characters * 3 RGB * 31 colours = 186
    
	for i=1,hci_numpals do
        -- vbank0 palette
		currentIP = {} 
		for j=0,47 do
			x=(i-1)*186 + j*2 + 1
			c1 = tnb(pal:sub(x,x),16)
			c2 = tnb(pal:sub(x+1,x+1),16)
			c = c2+16*c1
			table.insert(currentIP,c)	
		end
		table.insert(hci_lp,currentIP)

        -- vbank1 palette
        currentIP = {}
        for j=0,2 do
            table.insert(currentIP,0)
        end
        for j=48,92 do
			x=(i-1)*186 + j*2 + 1
			c1 = tnb(pal:sub(x,x),16)
			c2 = tnb(pal:sub(x+1,x+1),16)
			c = c2+16*c1
			table.insert(currentIP,c)	
		end
		table.insert(hci_lop,currentIP)
	end

	-- load image
	local width = #gfx / (hci_numpals * 2) -- 2 chars per pixel for 31 colours)
	local height = hci_numpals
	trace("width x height:"..width.."x"..height)
    hci_width = width
    hci_height = height

    -- TODO load image into single sheet infinite memory
    -- TODO load image into spritemap, 0-15 colours and 16-31 seperated for overdraw

end
function hci_update(ft)
	currentLP={}
	for i=0,135 do
		table.insert(currentLP,hci_lp[i+ 1])
	end
	currentLOP={}
	for i=0,135 do
		table.insert(currentLOP,hci_lop[i+ 1])
	end
end
function hci_draw(ft)
	local tnb=tonumber
	-- switch to correct bank etc
    vbank(0)
	cls(0)
    vbank(1)
	cls(0)

    -- pixel by pixel mode
    for i=0,hci_width*hci_height-1 do
        x=i*2 + 1
        c1 = tnb(gfx:sub(x,x),16)
        c2 = tnb(gfx:sub(x+1,x+1),16)
        c = c2+16*c1
        if c < 16 then 
            vbank(0)
            pix(i%hci_width,i//hci_width,c)
        else
            vbank(1)
            pix(i%hci_width,i//hci_width,c-15) -- assumes transparent OVR colour is 0
        end
    end

	-- make sure active scan is on
	activeScan=1
end

activeScan=1
currentP={}
currentOP={}
currentLP={}
currentLOP={}
function SCN(l)
	if activeScan == 1 then
        vbank(0)
		setPalette(currentLP[(l%#currentLP)+1])
        vbank(1)
		setPalette(currentLOP[(l%#currentLP)+1])
	elseif (l==0) then
        vbank(0)
		setPalette(currentP)
        vbank(1)
		setPalette(currentOP)
	end
end

hci_init()
function TIC()
hci_update(1)
hci_draw(1)
end