import vara.app.jklipper.utils.system.SystemDetector;
import vara.app.jklipper.utils.*;

public class test {
	
	public static void main(String ... args)throws Exception{
		
		System.out.println("Welcom in test application ! ;~}");
		System.out.println("SysInfo:"+ SystemDetector.getSystemFullName());

		System.out.println();
		System.out.println("Usage:" +
			"\n\tFirst parameter describe number of ms to sleep before exit." +
			"\n\tSecond parameter is exitcode.");

		int nArgs = args.length;
		int exitcode =0;

		System.out.println();
		
		String sArgs = Utilities.toString(args,",");
		System.out.println("Hello word "+test.class.getSimpleName()+" args["+sArgs+"]");
		
		if(nArgs>0){
			int sleep=Utilities.Numbers.parse(args[0],10);
			System.out.println("Internal: got to sleep "+sleep+"ms. ZzzZZZzzzZZZZzzZZzz...");
			Thread.sleep(sleep);
			
		}
		if(nArgs>1){
			exitcode =Utilities.Numbers.parse(args[1],0);
		}

		System.out.println("Application exit with exitcode:"+exitcode);
		System.out.println();
		System.exit(exitcode);
	}
}
