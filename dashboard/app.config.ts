export default defineAppConfig({
  ui: {
    primary: 'blue',
    gray: 'zinc',
    card: {
      background: 'bg-card',
      divide: 'divide-y divide-border/60',
      ring: 'ring-1 ring-border/80',
      shadow: 'shadow-sm',
      header: {
        padding: 'p-4 sm:p-5'
      },
      body: {
        padding: 'p-4 sm:p-5'
      },
      footer: {
        padding: 'p-4 sm:p-5'
      }
    },
    modal: {
      background: 'bg-card',
      overlay: {
        background: 'bg-black/75 backdrop-blur-sm'
      }
    },
    input: {
      color: {
        white: {
          outline: 'shadow-sm bg-background/80 text-foreground ring-1 ring-inset ring-border focus:ring-2 focus:ring-primary'
        }
      }
    },
    select: {
      color: {
        white: {
          outline: 'shadow-sm bg-background/80 text-foreground ring-1 ring-inset ring-border focus:ring-2 focus:ring-primary'
        }
      }
    },
    textarea: {
      color: {
        white: {
          outline: 'shadow-sm bg-background/80 text-foreground ring-1 ring-inset ring-border focus:ring-2 focus:ring-primary'
        }
      }
    }
  }
})
