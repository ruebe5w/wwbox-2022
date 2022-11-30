import wwbox
pl1=wwbox.Player("Pl1")
pl2=wwbox.Player("Pl2")
pl3=wwbox.Player("Pl3")
pl4=wwbox.Player("Pl4")
game=wwbox.WWGame([pl1,pl2,pl3,pl4],[wwbox.gameRoles.villager,wwbox.gameRoles.werewolf])
print(type(wwbox.gameRoles.villager))
game.init_game()
game.start_game()