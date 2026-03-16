#!/usr/bin/env python3
"""Control flow graph builder from simple imperative programs."""
import sys

class Block:
    def __init__(self,label):self.label=label;self.stmts=[];self.succs=[]
    def __repr__(self):return f"BB({self.label}): {self.stmts} -> {[s.label for s in self.succs]}"

class CFG:
    def __init__(self):self.blocks=[];self.entry=None
    def new_block(self,label=None):
        b=Block(label or f"bb{len(self.blocks)}")
        self.blocks.append(b)
        if not self.entry:self.entry=b
        return b
    def add_edge(self,src,dst):src.succs.append(dst)
    def dominators(self):
        doms={b:set(self.blocks) for b in self.blocks}
        doms[self.entry]={self.entry}
        changed=True
        while changed:
            changed=False
            for b in self.blocks:
                if b==self.entry:continue
                preds=[p for p in self.blocks if b in p.succs]
                if preds:
                    new=set.intersection(*(doms[p] for p in preds))|{b}
                else:new={b}
                if new!=doms[b]:doms[b]=new;changed=True
        return {b.label:sorted(d.label for d in ds) for b,ds in doms.items()}
    def to_dot(self):
        lines=["digraph CFG {"]
        for b in self.blocks:
            label="\\n".join([b.label]+b.stmts)
            lines.append(f'  {b.label} [label="{label}" shape=box];')
            for s in b.succs:lines.append(f"  {b.label} -> {s.label};")
        lines.append("}");return "\n".join(lines)

def build_cfg(stmts):
    cfg=CFG();cur=cfg.new_block("entry")
    for s in stmts:
        s=s.strip()
        if s.startswith("if"):
            then_b=cfg.new_block();else_b=cfg.new_block();merge=cfg.new_block()
            cur.stmts.append(s);cfg.add_edge(cur,then_b);cfg.add_edge(cur,else_b)
            cfg.add_edge(then_b,merge);cfg.add_edge(else_b,merge);cur=merge
        elif s.startswith("while"):
            header=cfg.new_block();body=cfg.new_block();exit_b=cfg.new_block()
            cfg.add_edge(cur,header);header.stmts.append(s)
            cfg.add_edge(header,body);cfg.add_edge(header,exit_b)
            cfg.add_edge(body,header);cur=exit_b
        else:
            cur.stmts.append(s)
    return cfg

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        cfg=build_cfg(["x = 1","if x > 0","y = 2","z = x + y"])
        assert len(cfg.blocks)==4  # entry, then, else, merge
        assert cfg.entry.label=="entry"
        doms=cfg.dominators()
        assert "entry" in doms["entry"]
        # while loop
        cfg2=build_cfg(["i = 0","while i < 10","i = i + 1"])
        assert len(cfg2.blocks)==4  # entry, header, body, exit
        assert any(b.label in [s.label for s in b.succs] for b in cfg2.blocks for _ in [0] if len(b.succs)>1)  # back edge exists
        print("All tests passed!")
    else:
        cfg=build_cfg(["x = 1","if x > 0","y = 2","z = x + y"])
        print(cfg.to_dot())
if __name__=="__main__":main()
