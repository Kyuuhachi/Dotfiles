function! s:is_scheme(stack)
	let scheme = 0
	for id in a:stack
		let name = synIDattr(id, 'name')
		if name =~# 'lilySchemeStruc.' || name =~# 'lilySchemeQuoted.' | let scheme = 1 | endif
		if name =~# 'lilySchemeLily.' | let scheme = 0 | endif
	endfor
	return scheme
endfunction


function! s:updateSubtype()
	let scheme = s:is_scheme(synstack(line('.'), col('.')))
	let line_scheme = s:is_scheme(synstack(line('.'), 1))
	if scheme != getbufvar("", "scheme", -1)
		let b:scheme = scheme
		if scheme
			setlocal iskeyword=33,35-38,42,43,45-58,60-90,94,95,97-122,126,_ lisp
		else
			setlocal iskeyword< nolisp
		endif
	endif
	if line_scheme != getbufvar("", "line_scheme", -1)
		let b:line_scheme = line_scheme
		if line_scheme
			setlocal commentstring=;\ %s
		else
			setlocal commentstring=%\ %s
		endif
	endif
endfunction
call s:updateSubtype()

augroup c98lilypond
	au!
	au CursorMoved,CursorMovedI *.ly call s:updateSubtype()
	au CursorHold,CursorHoldI *.ly call s:updateSubtype()
	au BufEnter *.ly call s:updateSubtype()
augroup END


let b:match_skip = 's:lilyComment\|lilyString\|lilySymbol\|lilyArticulation'
let b:match_words = "<<:>>,{:},\":\",<:>,\(:\),\[:\],(:),[:],\\temporary:\\revert"

let b:undo_ftplugin = 'setlocal indentexpr< ts< sts< sw< et< wig< | au! c98lilypond'
