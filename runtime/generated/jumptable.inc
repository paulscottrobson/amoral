;
;	Automatically generated
;
	.word LoadHandler              ; $80 LDR
	.word Andhandler               ; $81 AND
	.word Orhandler                ; $82 ORR
	.word Xorhandler               ; $83 XOR
	.word Addhandler               ; $84 ADD
	.word Subhandler               ; $85 SUB
	.word MultiplyHandler          ; $86 MLT
	.word DivideHandler            ; $87 DIV
	.word ModulusHandler           ; $88 MOD
	.word DecHandler               ; $89 DEC
	.word StoreHandler             ; $8a STR
	.word Branch_Always            ; $8b BRA
	.word Branch_Zero              ; $8c BEQ
	.word Branch_NonZero           ; $8d BNE
	.word Branch_Minus             ; $8e BMI
	.word Branch_Positive          ; $8f BPL
	.word Inc_Unary                ; $f0 INC
	.word Dec_Unary                ; $f1 DEC
	.word Shl_Unary                ; $f2 SHL
	.word Shr_Unary                ; $f3 SHR
	.word Clr_Unary                ; $f4 CLR
	.word Command_Return           ; $f5 RET
	.word OpcodeError              ; $f6 ?
	.word OpcodeError              ; $f7 ?
	.word OpcodeError              ; $f8 ?
	.word OpcodeError              ; $f9 ?
	.word OpcodeError              ; $fa ?
	.word OpcodeError              ; $fb ?
	.word OpcodeError              ; $fc ?
	.word OpcodeError              ; $fd ?
	.word OpcodeError              ; $fe ?
	.word OpcodeError              ; $ff ?
