-- title:  Display
-- author: Decca/Rift
-- desc:   show an indexed image
-- script: lua

-- CODEBLOCK

function tomem(dat,ofs,len)
    local y=0
    for x = 1,#dat,1 do -- write to mem
        local c=tonumber(dat:sub(x,x),16) -- get (c)olor value
        poke4(ofs+y,c) y=y+1
        if y>len then y=0 ofs=ofs+240 end
    end
end

-- write to memory
tomem(pal,32640,95)
tomem(gfx,0,res)

function TIC()

end