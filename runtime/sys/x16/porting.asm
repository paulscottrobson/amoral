; *******************************************************************************************
; *******************************************************************************************
;
;       File:           porting.asm
;       Date:           14th November 2020
;       Purpose:        System specific code (X16)
;       Author:         Paul Robson (paul@robson.org.uk)
;
; *******************************************************************************************
; *******************************************************************************************

Vera = $9F20

; *******************************************************************************************
;
;									Print Character
;
; *******************************************************************************************

		define 	"print.character:1",EndPrintCharacter
PrintCharacter:
		phxa
		jsr 	$FFD2
		plxa
		rts
EndPrintCharacter:

; *******************************************************************************************
;
;									Print CR/LF
;
; *******************************************************************************************

		define 	"print.crlf:0",EndPrintCRLF
		pha
		lda 	#13
		jsr 	PrintCharacter
		pla
		rts
EndPrintCRLF:

; *******************************************************************************************
;
;									Read 60Hz Clock.
;
; *******************************************************************************************

		define 	"read.timer:0",EndReadTimer
ReadTimer:
		jsr 	$FFDE						; the documentation is mostly wrong it's YXA.
		rts

EndReadTimer:

; *******************************************************************************************
;
;								  Quit X16 Emulator
;
; *******************************************************************************************

		define 	"exit.emulator:0",EndExitEmulator
		jmp 	$FFFF
EndExitEmulator:

; *******************************************************************************************
;
;								  VPoke bank,addr,data
;
; *******************************************************************************************

		define "poke.v:3",EndVPoke
		tay 								; save byte in Y
		lda 	Param1 						; set Vera address
		sta 	Vera+2
		lda 	Param2+1
		sta 	Vera+1
		lda 	Param2
		sta 	Vera
		sty 	Vera+3
		tya
		rts
EndVPoke:		

		define "poke.vw:3",EndVWPoke
		tay 								; save byte in Y
		lda 	Param1 						; set Vera address
		ora 	#$10 						; set 1 increment
		sta 	Vera+2
		lda 	Param2+1
		sta 	Vera+1
		lda 	Param2
		sta 	Vera
		sty 	Vera+3 						; write out a word.
		stx 	Vera+3 
		tya
		rts
EndVWPoke:	

		define "peek.v:2",EndVPeek
		stx 	Vera+1
		sta 	Vera
		lda 	Param1
		sta 	Vera+2
		lda 	Vera+3
		ldx 	#0
		rts
EndVPeek:
