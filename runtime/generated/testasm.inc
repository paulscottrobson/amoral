;
;	Automatically generated
;
TEST_count:
	.byte $80,$41                                  ; ldr #65
	.byte $aa,$00                                  ; str [0]
	.byte $90,$ff,$7f                              ; ldr #32767
	.byte $aa,$02                                  ; str [2]
	.byte $ff                                      ; halt 
